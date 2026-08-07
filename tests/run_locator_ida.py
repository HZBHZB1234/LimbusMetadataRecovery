#!/usr/bin/env python3
"""run_locator_ida.py - IDA MCP 后台执行定位器（由 py_exec_file 调用）。

用法（MCP）：py_exec_file 本文件；通过环境变量 LIMBUS_LOCATOR_OUT 控制输出。
"""
import os
import sys
from pathlib import Path

repo = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(repo / "tools"))

sys.modules.pop("locate_metadata_init", None)
sys.modules.pop("report", None)

from locate_metadata_init import run_background  # noqa: E402

out_dir = Path(os.environ.get("LIMBUS_LOCATOR_OUT", repo / "out" / "locator-08-06"))
run_background(out_dir, top_k=20, max_decompile=400)
print("DONE")
