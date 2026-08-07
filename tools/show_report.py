#!/usr/bin/env python3
"""show_report.py - 快速查看验证/提取报告（开发辅助）。"""
import json
import sys
from pathlib import Path


def main() -> int:
    for path in sys.argv[1:]:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        print(f"== {path}  verdict={data.get('verdict')}")
        for g in data.get("gates", []):
            print(("PASS" if g["passed"] else "FAIL"), g["name"], "|", g["evidence"][:110])
        for r in data.get("review_items", []):
            print("REVIEW", r["id"], r["question"], "|", r["evidence"][:80])
        secs = data.get("sections", {}).get("sections")
        if secs:
            for s in secs:
                print(f"  sec[{s['index']}] {s.get('name','')} size_off={s.get('size_off')} "
                      f"off_off={s.get('offset_off')} adj={s.get('adj')} "
                      f"kind={s.get('kind')} ev={s.get('evidence')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
