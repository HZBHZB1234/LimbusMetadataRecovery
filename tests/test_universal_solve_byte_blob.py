#!/usr/bin/env python3
"""回归守卫：字节流节 size==count 时 RecOf 误判为整数 rec，rec=None 槽位仍须能选中它。

对应 2026-10-29 版失效根因：attributeData 恰 size==count（2234324）被
_rec_of 判为 rec=1，导致 rec=None 的字节流槽位永远选不到它，尾段整链无解
（"无可行锚点槽位组合"）。此前各版 size!=count 未触发。

纯 Python 依赖，秒级。用法：python tests/test_universal_solve_byte_blob.py
"""

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from universal.solve_versioned import _rec_of, _slot_candidates


def main() -> int:
    checks = []

    # 1) 诱发条件本身：size==count 的字节 blob 被 _rec_of 判为整数 rec=1
    attr = {"index": 80, "size": 2234324, "count": 2234324, "offset": 0}
    checks.append(("_rec_of(size==count) == 1", _rec_of(attr) == 1))

    # 2) rec=None 槽位必须仍能选中该字节 blob（修复核心）
    vtbl = {"index": 36, "size": 13098732, "count": 3274683, "offset": 0}  # rec=4
    pool = {1: [], 4: [vtbl], None: []}
    checks.append(("rec=None 槽位包含 size==count blob",
                   attr in _slot_candidates(None, pool, [attr])))

    # 3) 整数 rec 槽位不受污染：绝不把 size==count 字节 blob 混入
    checks.append(("rec=4 槽位不含该 blob",
                   attr not in _slot_candidates(4, pool, [attr])))
    checks.append(("rec=4 槽位仍返回其固定记录条目",
                   _slot_candidates(4, pool, [attr]) == [vtbl]))

    # 4) 常规 rec=None 条目（size%count!=0）不受影响、照常保留
    sld = {"index": 76, "size": 931799, "count": 32187, "offset": 0}
    checks.append(("size%count != 0 -> _rec_of None", _rec_of(sld) is None))
    checks.append(("rec=None 保留普通 None 条目",
                   _slot_candidates(None, {None: [sld]}, []) == [sld]))

    ok = all(v for _, v in checks)
    for name, v in checks:
        print(f"[{'PASS' if v else 'FAIL'}] {name}")
    print("verdict:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
