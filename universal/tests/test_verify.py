#!/usr/bin/env python3
"""test_verify.py - 无参考结构验证回归（08-13 / 08-06）。

链路：DLL → locate → extract（指令级）→ layouts/verify（结构门）。
验证结果为 PASS 即证明提取参数真实有效。
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from universal.pe_loader import load_pe
from universal.init_locator import function_start_of, disasm_func
from universal.xorshift_scan import scan_pe
from universal.extract_disasm import extract_from_disasm
from universal.verify_structural import verify

DLL_08_13 = r"C:\Program Files (x86)\Steam\steamapps\common\Limbus Company\GameAssembly.dll"
MD_08_13 = r"C:\Program Files (x86)\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\il2cpp_data\Metadata\global-metadata.dat"
DLL_08_06 = r"E:\desktop\work\LimbusDecompile\samples\steam-2026-08-06\GameAssembly.dll"
MD_08_06 = r"E:\desktop\work\LimbusDecompile\samples\steam-2026-08-06\global-metadata.dat"
TRUTH_EA = 0x18069C5E0


def check(dll_path: str, md_path: str, label: str) -> int:
    image = load_pe(dll_path)
    hits = scan_pe(image)
    start = function_start_of(min(hits), image)
    if start != TRUTH_EA:
        print(f"[{label}] func start mismatch: FAIL")
        return 1
    ext = extract_from_disasm(image, start)
    profile = ext.to_profile()
    if ext.errors:
        print(f"[{label}] extract errors: {ext.errors}")
        return 1
    metadata = open(md_path, "rb").read()
    res = verify(metadata, profile)
    print(f"[{label}] verdict={res['verdict']} layout={res['layout']['best']} "
          f"score={res['layout']['scores'][res['layout']['best']]:.3f}")
    for g in res["gates"]:
        print(f"   [{'PASS' if g['passed'] else 'FAIL'}] {g['name']}: {g['evidence']}")
    for s in res.get("sections", []):
        print(f"   sec{s['index']}: kind={s.get('kind')} phys={s.get('physical_offset')} "
              f"size={s.get('header_size')}")
    return 0 if res["verdict"] == "PASS" else 1


def main() -> int:
    rc = 0
    if Path(DLL_08_13).exists():
        rc |= check(DLL_08_13, MD_08_13, "08-13")
    if Path(DLL_08_06).exists():
        rc |= check(DLL_08_06, MD_08_06, "08-06")
    return rc


if __name__ == "__main__":
    sys.exit(main())
