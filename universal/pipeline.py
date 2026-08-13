#!/usr/bin/env python3
"""pipeline.py - universal 解密管线编排（版本无关，无参考文件）。

用法：
  python -m universal.pipeline --dll <GameAssembly.dll> --metadata <global-metadata.dat>
                              [--version 39] [--out-dir out] [--name steam]

阶段：
  1. locate   ：xorshift 字节模板扫描 + 反汇编特征评分（无 IDA）
  2. extract  ：指令级参数提取（header_size/seed/表/7 节，无文本正则）
  3. verify   ：无参考结构验证（布局自动判定 + 解密结构门）
  4. solve    ：无参考 31 节映射（锚点间隙链拼装 + 内容签名）
  5. rebuild  ：标准文件重建 + 四重自验证
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

from .extract_disasm import extract_from_disasm
from .init_locator import function_start_of, locate
from .pe_loader import load_pe
from .rebuild_validate import rebuild_standard, validate_standard
from .solve_versioned import solve
from .verify_structural import verify
from .xorshift_scan import scan_pe

TRUTH_INIT = 0x18069C5E0  # 07-30/08-06/08-13 三版实测 init 地址（仅测试断言用）


def run(dll_path: str, metadata_path: str, version: int = 39,
        out_dir: Path = Path("out"), name: str = "universal") -> dict:
    t0 = time.time()
    report: dict = {"version": version, "stages": {}, "verdicts": {}}
    out_dir.mkdir(parents=True, exist_ok=True)

    # ---- 1. 定位 -----------------------------------------------------------
    image = load_pe(dll_path)
    hits = scan_pe(image)
    cands = locate(image, top_k=5)
    report["stages"]["locate"] = {
        "xorshift_hits": len(hits),
        "candidates": cands,
        "top1": cands[0]["ea"] if cands else None,
    }
    report["verdicts"]["locate"] = "PASS" if cands else "FAIL"
    if not cands:
        return report
    init_va = cands[0]["ea"]

    # ---- 2. 提取 -----------------------------------------------------------
    ext = extract_from_disasm(image, init_va)
    profile = ext.to_profile()
    report["stages"]["extract"] = {
        "func_ea": init_va,
        "header_size": ext.header_size,
        "header_seed": ext.header_seed and f"0x{ext.header_seed:X}",
        "table_addr": ext.table_addr,
        "sections": ext.sections,
        "errors": ext.errors,
    }
    report["verdicts"]["extract"] = "PASS" if not ext.errors else "FAIL"
    if ext.errors:
        return report

    # ---- 3. 验证 -----------------------------------------------------------
    metadata = Path(metadata_path).read_bytes()
    vres = verify(metadata, profile)
    report["stages"]["verify"] = {
        "layout": vres.get("layout", {}).get("best"),
        "gates": vres.get("gates", []),
    }
    report["verdicts"]["verify"] = vres["verdict"]

    # ---- 4. 求解 -----------------------------------------------------------
    try:
        solution = solve(metadata, profile, version=version)
        report["stages"]["solve"] = {
            "layout": solution.get("layout"),
            "anchor_slots": solution.get("anchor_slots"),
            "protected": solution.get("protected"),
            "review": solution.get("review", []),
        }
        report["verdicts"]["solve"] = "PASS" if not solution.get("review") else "REVIEW"
    except Exception as e:  # noqa: BLE001
        report["stages"]["solve"] = {"error": str(e)}
        report["verdicts"]["solve"] = "FAIL"
        return report

    # ---- 5. 重建 + 自验证 --------------------------------------------------
    std = rebuild_standard(metadata, solution, profile["table_hex"], version=version)
    gates = validate_standard(std, solution, metadata, profile["table_hex"], version=version)
    report["stages"]["rebuild"] = {
        "size": len(std),
        "gates": gates,
    }
    report["verdicts"]["rebuild"] = "PASS" if all(g["passed"] for g in gates) else "FAIL"

    std_path = out_dir / f"{name}-standard.dat"
    std_path.write_bytes(std)
    (out_dir / f"{name}-profile.json").write_text(
        json.dumps({**profile, "solution": solution}, indent=1, ensure_ascii=False),
        encoding="utf-8")
    report["outputs"] = {
        "standard": str(std_path),
        "profile": str(out_dir / f"{name}-profile.json"),
    }
    report["elapsed_sec"] = round(time.time() - t0, 1)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="universal metadata 解密管线")
    parser.add_argument("--dll", required=True, help="GameAssembly.dll 路径")
    parser.add_argument("--metadata", required=True, help="加密 global-metadata.dat")
    parser.add_argument("--version", type=int, default=39, help="IL2CPP metadata 版本")
    parser.add_argument("--out-dir", type=Path, default=Path("out"))
    parser.add_argument("--name", default="universal")
    args = parser.parse_args()

    report = run(args.dll, args.metadata, args.version, args.out_dir, args.name)
    print(json.dumps(report, indent=1, ensure_ascii=False))
    verdicts = report.get("verdicts", {})
    ok = all(v in ("PASS", "REVIEW") for v in verdicts.values()) and bool(verdicts)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
