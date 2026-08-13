#!/usr/bin/env python3
"""test_locator.py - init_locator 真值回归（08-13 / 08-06 样本）。

真值：两个版本的 init 均为 sub_18069C5E0（RVA 0x69C5E0）。
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from universal.pe_loader import load_pe
from universal.xorshift_scan import scan_pe
from universal.init_locator import locate

DLL_08_13 = r"C:\Program Files (x86)\Steam\steamapps\common\Limbus Company\GameAssembly.dll"
DLL_08_06 = r"E:\desktop\work\LimbusDecompile\samples\steam-2026-08-06\GameAssembly.dll"

TRUTH_EA = 0x18069C5E0


def check(dll_path: str, label: str) -> int:
    image = load_pe(dll_path)
    hits = scan_pe(image)
    print(f"[{label}] xorshift template hits: {len(hits)}")
    cands = locate(image, top_k=5)
    for i, c in enumerate(cands[:5]):
        mark = " <== TRUTH" if c["ea"] == TRUTH_EA else ""
        print(f"  rank{i + 1}: 0x{c['ea']:X} score={c['score']} "
              f"loops={c['xorshift_loops']} oword={c['oword']} "
              f"imm64={c['imm64']} table_ref={c['table_ref']} "
              f"gwrite={c['global_write']}{mark}")
    ok = bool(cands) and cands[0]["ea"] == TRUTH_EA
    print(f"[{label}] top1 == 0x{TRUTH_EA:X}: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    rc = 0
    if Path(DLL_08_13).exists():
        rc |= check(DLL_08_13, "08-13")
    if Path(DLL_08_06).exists():
        rc |= check(DLL_08_06, "08-06")
    return rc


if __name__ == "__main__":
    sys.exit(main())
