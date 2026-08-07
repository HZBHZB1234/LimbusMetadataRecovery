# -*- coding: utf-8 -*-
"""metadata_locator_plugin.py - 解密入口定位器 IDA 插件。

替代 metadata_trace.py 的脆弱"首个引用"链：证据驱动候选评分。
热键：Ctrl-Alt-Shift-M（与旧插件的 Ctrl-Alt-M 不冲突）。
输出：<IDB 目录>/locator_out/locate_candidates.json + 报告。

安装：复制到 IDA plugins 目录（如 C:\\Program Files\\IDA Professional 9.3\\plugins\\）。
"""

import os
import sys
from pathlib import Path

import idaapi
import ida_kernwin

_plugin_dir = Path(__file__).resolve().parent
if str(_plugin_dir) not in sys.path:
    sys.path.insert(0, str(_plugin_dir))
if str(_plugin_dir / "tools") not in sys.path:
    sys.path.insert(0, str(_plugin_dir / "tools"))

import locate_metadata_init  # noqa: E402


class LocateMetadataInitPlugin(idaapi.plugin_t):
    flags = idaapi.PLUGIN_KEEP
    comment = "Locate metadata decrypt init function via evidence scoring"
    help = "Scan xorshift patterns + decompile features, rank candidates"
    wanted_name = "Locate Metadata Init"
    wanted_hotkey = "Ctrl-Alt-Shift-M"

    def init(self):
        return idaapi.PLUGIN_OK

    def run(self, arg):
        out_dir = Path(idaapi.get_root_filename()).parent / "locator_out"
        env = os.environ.get("LIMBUS_LOCATOR_OUT")
        if env:
            out_dir = Path(env)
        try:
            locate_metadata_init.run_background(out_dir, top_k=20)
            ida_kernwin.info(f"定位器完成：{out_dir / 'locate_candidates.json'}")
        except Exception as exc:  # noqa: BLE001
            ida_kernwin.warning(f"定位器失败：{exc}")

    def term(self):
        pass


def PLUGIN_ENTRY():
    return LocateMetadataInitPlugin()
