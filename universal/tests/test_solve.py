#!/usr/bin/env python3
"""test_solve.py - 无参考求解回归（08-13 / 08-06）。

08-06：31 节映射与 profiles/steam-2026-08-06.json 逐项一致（真值全量比对）。
08-13：受保护节命名 + 重建标准通过四重自验证；与 gen1 08-13 求解的
已定位非保护节物理位置交叉抽查。
"""

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from universal.pe_loader import load_pe
from universal.init_locator import function_start_of
from universal.xorshift_scan import scan_pe
from universal.extract_disasm import extract_from_disasm
from universal.solve_versioned import solve
from universal.rebuild_validate import rebuild_standard, validate_standard
from universal.versions import V39_NAMES

DLL_08_13 = r"C:\Program Files (x86)\Steam\steamapps\common\Limbus Company\GameAssembly.dll"
MD_08_13 = r"C:\Program Files (x86)\Steam\steamapps\common\Limbus Company\LimbusCompany_Data\il2cpp_data\Metadata\global-metadata.dat"
DLL_08_06 = r"E:\desktop\work\LimbusDecompile\samples\steam-2026-08-06\GameAssembly.dll"
MD_08_06 = r"E:\desktop\work\LimbusDecompile\samples\steam-2026-08-06\global-metadata.dat"
PROFILE_08_06 = r"E:\desktop\work\LimbusDecompile\profiles\steam-2026-08-06.json"
TRUTH_EA = 0x18069C5E0
EXPECT_SHA_08_06 = "73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7"

# gen1 solve-08-13 已定位的非保护节物理位置（交叉抽查）
GEN1_08_13_LOCATED = {
    "events": 5697016, "parameterDefaultValues": 15727992,
    "fieldDefaultValues": 15855288, "fieldAndParameterDefaultValueData": 16414660,
    "parameters": 18923604, "genericParameters": 25086456,
    "genericContainers": 25207464, "nestedTypes": 25285016,
    "typeDefinitions": 37203108, "images": 41000612,
    "referencedAssemblies": 41028516, "attributeDataRange": 42805240,
    "unresolvedVirtualCallParameterRanges": 43590200,
}


def run_pipeline(dll_path: str, md_path: str) -> tuple[dict, dict, bytes]:
    image = load_pe(dll_path)
    hits = scan_pe(image)
    start = function_start_of(min(hits), image)
    ext = extract_from_disasm(image, start)
    if ext.errors:
        raise RuntimeError(f"extract errors: {ext.errors}")
    profile = ext.to_profile()
    metadata = open(md_path, "rb").read()
    solution = solve(metadata, profile)
    std = rebuild_standard(metadata, solution, profile["table_hex"])
    return solution, profile, std


def check_08_06() -> int:
    truth = json.load(open(PROFILE_08_06, encoding="utf-8"))
    expected = {s["name"]: (s["custom_entry_index"], s["physical_offset_adjustment"])
                for s in truth["standard_sections"]}
    solution, profile, std = run_pipeline(DLL_08_06, MD_08_06)
    mismatches = []
    for name, (eidx, adj) in expected.items():
        got = solution["sections"].get(name)
        if not got:
            mismatches.append(f"{name}: 缺失")
            continue
        if got["custom_entry_index"] != eidx:
            mismatches.append(f"{name}: entry {got['custom_entry_index']} != {eidx}")
        if got["physical_offset_adjustment"] != adj:
            mismatches.append(f"{name}: adj {got['physical_offset_adjustment']} != {adj}")
    print(f"[08-06] 31 节映射逐项一致: {'PASS' if not mismatches else 'FAIL'}")
    for m in mismatches[:10]:
        print("   ", m)
    gates = validate_standard(std, solution, open(MD_08_06, "rb").read(),
                              profile["table_hex"])
    for g in gates:
        print(f"   [{'PASS' if g['passed'] else 'FAIL'}] {g['name']}: {g['evidence']}")
    sha = hashlib.sha256(std).hexdigest().upper()
    sha_ok = sha == EXPECT_SHA_08_06
    print(f"[08-06] 重建 SHA-256: {'PASS' if sha_ok else 'FAIL'} {sha}")
    ok = not mismatches and all(g["passed"] for g in gates) and sha_ok
    return 0 if ok else 1


def check_08_13() -> int:
    solution, profile, std = run_pipeline(DLL_08_13, MD_08_13)
    print(f"[08-13] layout={solution['layout']}")
    prot_note = ", ".join(f"{n}@{p['entry_index']}" for n, p in solution["protected"].items())
    print(f"[08-13] protected: {prot_note}")
    cross = []
    for name, phys in GEN1_08_13_LOCATED.items():
        got = solution["sections"].get(name)
        p = got and solution["evidence"].get(name, {}).get("physical")
        if p is None or abs(p - phys) > 0x1000:
            cross.append(f"{name}: got={p} want={phys}")
    print(f"[08-13] gen1 交叉抽查: {'PASS' if not cross else 'FAIL'}")
    for c in cross:
        print("   ", c)
    gates = validate_standard(std, solution, open(MD_08_13, "rb").read(),
                              profile["table_hex"])
    for g in gates:
        print(f"   [{'PASS' if g['passed'] else 'FAIL'}] {g['name']}: {g['evidence']}")
    sha = hashlib.sha256(std).hexdigest().upper()
    print(f"[08-13] rebuilt sha256={sha} size={len(std)}")
    ok = not cross and all(g["passed"] for g in gates) and not solution["review"]
    return 0 if ok else 1


def main() -> int:
    rc = 0
    if Path(DLL_08_06).exists():
        rc |= check_08_06()
    if Path(DLL_08_13).exists():
        rc |= check_08_13()
    return rc


if __name__ == "__main__":
    sys.exit(main())
