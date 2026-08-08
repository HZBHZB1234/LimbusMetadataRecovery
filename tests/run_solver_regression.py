#!/usr/bin/env python3
"""solve_section_map 的 08-06 端到端回归。

验收（DESIGN_SECTION_SOLVER.md 第七节）：
1. 输出映射与 profiles/steam-2026-08-06.json 的 standard_sections 逐项一致
   （31 个 custom_entry_index + physical_offset_adjustment 全同）。
2. 相 4 重建 SHA-256 == 73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7。
3. requires_review == 0。
"""

import json
import os
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "tools"))

from solve_section_map import solve
from report import Report

EXPECT_SHA = "73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7"
MAIN = Path(os.environ.get("LIMBUS_MAIN_DIR", r"E:\desktop\work\LimbusDecompile"))
METADATA = MAIN / "samples" / "steam-2026-08-06" / "global-metadata.dat"
CANDIDATE = REPO / "out" / "candidate_profile_08_06.json"
REFERENCE = MAIN / "analysis" / "global-metadata-standard-steam-2026-08-06.dat"
PROFILE = MAIN / "profiles" / "steam-2026-08-06.json"
OUT_DIR = REPO / "out"


def main() -> int:
    import hashlib

    from solve_section_map import parse_reference, rebuild_standard, decrypt_header

    metadata = METADATA.read_bytes()
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    reference = parse_reference(REFERENCE.read_bytes())
    profile = json.loads(PROFILE.read_text(encoding="utf-8"))

    rep = Report(tool="solve_section_map_regression",
                 version="steam-2026-08-06", title="求解器 08-06 回归")

    solution = solve(metadata, candidate, reference, rep)
    if not solution:
        rep.gate("求解完成", False, "solve 返回空")
        rep.write_all(OUT_DIR, "regression-08-06")
        print("FAIL: solve returned empty")
        return 1

    solved = solution["sections"]
    expected = {s["name"]: s for s in profile["standard_sections"]}

    mismatches = []
    for name, exp in expected.items():
        got = solved.get(name)
        if not got:
            mismatches.append(f"{name}: 缺失")
            continue
        if got["custom_entry_index"] != exp["custom_entry_index"]:
            mismatches.append(
                f"{name}: entry {got['custom_entry_index']} != {exp['custom_entry_index']}")
        if got["physical_offset_adjustment"] != exp["physical_offset_adjustment"]:
            mismatches.append(
                f"{name}: adj {got['physical_offset_adjustment']} != {exp['physical_offset_adjustment']}")
    rep.gate("映射与 profile 逐项一致", not mismatches,
             "; ".join(mismatches) or "31 节全同")
    rep.gate("requires_review == 0", len(rep.review_items) == 0,
             f"review={len(rep.review_items)}")

    entries, _layout, table = decrypt_header(metadata, candidate)
    rebuilt = rebuild_standard(metadata, entries, table, solution, reference["version"])
    actual_sha = hashlib.sha256(rebuilt).hexdigest().upper()
    rep.gate("重建 SHA-256", actual_sha == EXPECT_SHA,
             f"{actual_sha} == {EXPECT_SHA}")
    out_path = OUT_DIR / "standard-rebuilt-08-06.dat"
    out_path.write_bytes(rebuilt)
    rep.set_section("result", {
        "solved": solved,
        "sha256": actual_sha,
        "rebuilt": str(out_path),
    })

    # ---- apply 提升闭环：生成正式 profile 并自检重建 --------------------
    sys.path.insert(0, str(REPO / "tools"))
    from apply_profile import build_profile
    from solve_section_map import parse_reference as _pr
    generated = build_profile(metadata, candidate, solution, reference,
                              "steam-2026-08-06")
    from solve_section_map import rebuild_standard as _rs, decrypt_header as _dh
    gen_entries, _l, gen_table = _dh(metadata, candidate)
    gen_solution = {
        "sections": {s["name"]: {"custom_entry_index": s["custom_entry_index"],
                                 "physical_offset_adjustment": s["physical_offset_adjustment"]}
                     for s in generated["standard_sections"]},
        "protected": {p["name"]: {"seed": p["seed"]}
                      for p in generated["protected_sections"]},
    }
    gen_rebuilt = _rs(metadata, gen_entries, gen_table, gen_solution, reference["version"])
    gen_sha = hashlib.sha256(gen_rebuilt).hexdigest().upper()
    rep.gate("apply 生成 profile 自检 SHA-256", gen_sha == EXPECT_SHA,
             f"{gen_sha} == {EXPECT_SHA}")
    gen_path = OUT_DIR / "steam-2026-08-06.generated.json"
    gen_path.write_text(json.dumps(generated, indent=1, ensure_ascii=False),
                        encoding="utf-8")
    rep.gate("apply profile 字段",
             all(k in generated for k in ("header", "substitution_table_hex",
                                          "protected_sections", "standard_sections",
                                          "metadata_size", "metadata_sha256")),
             f"output={gen_path}")
    rep.write_all(OUT_DIR, "regression-08-06")

    ok = not mismatches and actual_sha == EXPECT_SHA
    print(f"verdict: {rep.verdict()}  map_ok={not mismatches} sha_ok={actual_sha == EXPECT_SHA}")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
