#!/usr/bin/env python3
"""test_extract.py - extract_disasm 真值回归（08-13 / 08-06）。

真值来自已验证的 profile（gen1 candidate_verify PASS 的 08-13 参数
与 profiles/steam-2026-08-06.json）。
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from universal.pe_loader import load_pe
from universal.init_locator import function_start_of, disasm_func
from universal.xorshift_scan import scan_pe
from universal.extract_disasm import extract_from_disasm

DLL_08_13 = r"C:\Program Files (x86)\Steam\steamapps\common\Limbus Company\GameAssembly.dll"
DLL_08_06 = r"E:\desktop\work\LimbusDecompile\samples\steam-2026-08-06\GameAssembly.dll"
TRUTH_EA = 0x18069C5E0

TRUTH_08_13 = {
    "header_size": 1236,
    "header_seed": 0x30FBE73A8992293E,
    "table_addr": "0x187355000",
    "sections": [
        (452, 448, -6512, 0xCD371567CB7722AA),
        (416, 412, 7336, 0xCA335BE4CCB9844),
        (1004, 1000, -7500, 0xC5306267CEF471C8),
        (1232, 1228, -2268, 0xD2FB2F77402CAFDD),
        (704, 700, 4468, 0xDC5E21DDF0866AE3),
        (1016, 1012, 1040, 0x1927ACB4476B3A93),
        (116, 112, -7948, 0xDFAF6B0F88AF8314),
    ],
}

TRUTH_08_06 = {
    "header_size": 1044,
    "header_seed": 0xBC41EAFC33962B00,
    "table_addr": "0x187356110",
    "sections": [
        (1024, 1020, -1508, 0x116C4B46EACABA5),
        (664, 660, 3476, 0xD4C07427B74C818E),
        (964, 960, -6696, 0xAFDAE7074F40F834),
        (136, 132, 4304, 0xA28BFC303CE665BA),
        (592, 588, -3984, 0xFF3532DDAC34BA66),
        (652, 648, -7080, 0x1DFCEDD20A3EE02C),
        (4, 0, 2268, 0x88942C9716431E06),
    ],
}


def check(dll_path: str, label: str, truth: dict) -> int:
    image = load_pe(dll_path)
    hits = scan_pe(image)
    start = function_start_of(min(hits), image)
    if start != TRUTH_EA:
        print(f"[{label}] func start 0x{start:X} != 0x{TRUTH_EA:X}: FAIL")
        return 1
    ext = extract_from_disasm(image, start)
    checks = {
        "header_size": ext.header_size == truth["header_size"],
        "header_seed": ext.header_seed == truth["header_seed"],
        "table_addr": ext.table_addr == truth["table_addr"],
        "no errors": not ext.errors,
    }
    ok = True
    print(f"[{label}] header_size={ext.header_size} seed={ext.header_seed and hex(ext.header_seed)} "
          f"table={ext.table_addr} sections={len(ext.sections)}")
    if len(ext.sections) != len(truth["sections"]):
        print(f"[{label}] sections count mismatch: FAIL")
        ok = False
    for idx, (size_off, offset_off, adj, seed) in enumerate(truth["sections"]):
        if idx >= len(ext.sections):
            ok = False
            continue
        got = ext.sections[idx]
        got_seed = int(got["seed"], 16) if got["seed"] else None
        m = (got["size_off"] == size_off and got["offset_off"] == offset_off
             and got["adj"] == adj and got_seed == seed)
        if not m:
            ok = False
            print(f"[{label}] s[{idx}] got=({got['size_off']},{got['offset_off']},"
                  f"{got['adj']},{got['seed']}) want=({size_off},{offset_off},{adj},{hex(seed)})")
    if ext.errors:
        print(f"[{label}] errors: {ext.errors}")
        ok = False
    for name, passed in checks.items():
        if not passed:
            ok = False
            print(f"[{label}] {name}: FAIL")
    print(f"[{label}] verdict: {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


def main() -> int:
    rc = 0
    if Path(DLL_08_13).exists():
        rc |= check(DLL_08_13, "08-13", TRUTH_08_13)
    if Path(DLL_08_06).exists():
        rc |= check(DLL_08_06, "08-06", TRUTH_08_06)
    return rc


if __name__ == "__main__":
    sys.exit(main())
