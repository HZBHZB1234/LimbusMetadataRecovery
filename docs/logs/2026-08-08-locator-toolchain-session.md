# 2026-08-08：metadata 解密入口定位三件套 + 求解器设计（本仓库初始会话）

## 报告目的

本仓库（`metadata-recovery/`）的首个会话。完成"解密入口定位 → 参数自动提取 →
候选验证"三件套并在 08-06 真实 IDB 上端到端全通；交付 31 段映射求解器设计文档。
主工作区 `LimbusDecompile`（`E:\desktop\work\LimbusDecompile`）与本文档互相引用，
大型样本/IDB/导出产物仍留在主工作区归档。

## 一、背景与动机

主工作区 `docs/FINDINGS.md` F-0004 已确认旧 `metadata_trace.py`（IDA 插件，
"首个字符串引用 → 首个调用者"）依赖枚举顺序、跨版本脆弱。本会话实现其替代方案：
**证据驱动的全函数候选评分 + 验证闭环**，定位是否正确由"提取参数能否重建出合法
metadata"裁决，而非模式相似度。

## 二、关键决策

1. 新仓库独立 git 历史，不污染主工作区；`out/`、样本、IDB 全部 gitignore。
2. 双入口：核心纯函数 + MCP 后台（`py_exec_file` 无人值守）+ 插件壳
   （Ctrl-Alt-Shift-M，与旧插件 Ctrl-Alt-M 不冲突）。
3. 提取器全自动正则，模式失败进 `requires_review` 而非静默输出。
4. 验证闭环不依赖完整 profile：布局双候选打分 + 节段结构门（text/index/binary）。
5. 31 段求解器本期只交付设计文档（`docs/DESIGN_SECTION_SOLVER.md`），实现为下一阶段。

## 三、实现组件

| 组件 | 文件 | 说明 |
| --- | --- | --- |
| 报告框架 | `tools/report.py` | gate/review/sections，裁决 PASS / PASS_WITH_REVIEW / FAIL |
| 定位器 | `tools/locate_metadata_init.py` | 粗筛：.text 单遍 xorshift64(13,7,17) 字节模式；精评：反编译特征 F1/F3/F5 + 全局写-读扇出 F2（反编译文本正则提取全局名，避免逐指令 xref 爆炸） |
| 插件 | `metadata_locator_plugin.py` | 定位器插件入口，输出到 IDB 目录 `locator_out/` |
| 提取器 | `tools/extract_decrypt_params.py` | 正则提取 header_size/header_seed/table/7 节 {size_off,offset_off,adj,seed}，兼容 07-30 memmove 与 08-06 封装拷贝+for 循环两种风格 |
| 验证闭环 | `tools/candidate_verify.py` | header 解密 + 布局自动判定 + 7 节段范围/解密/结构门 |
| 求解器设计 | `docs/DESIGN_SECTION_SOLVER.md` | 四相算法：记录大小匹配 → 内容指纹定位 → 链装配 → 重建验证 |

## 四、回归证据（08-06 真实 IDB，`samples/steam-2026-08-06/GameAssembly.dll.i64`）

### 定位器

- top-1 = `sub_18069C5E0`（profile 记录的真值 init），score 161.0，xorshift_loops 52、
  imm64 8、table_ref 13、oword 18、fanout 330；裁决 PASS。
- 提取的反编译文本 `out/locator-08-06/decompile_rank1_sub_18069C5E0.c` 已固化到
  `tests/fixtures/metadata_initialize_08-06.c` 作回归夹具。

### 提取器（夹具断言 66 项全过）

07-30 夹具（`tests/fixtures/metadata_initialize_current.c`，来自主工作区
`analysis/ida/metadata_initialize_current.c`）：header 0x2F4/seed `0xE039BA990B051CD7`/
表 `0x18759C190`，7 节逐项匹配 `profiles/steam-2026-07-30.json`。

08-06 夹具：header 1044/seed `0xBC41EAFC33962B00`/表 `0x187356110`，7 节
`{size_off, offset_off, adj, seed}` 逐项匹配 `profiles/steam-2026-08-06.json`：

| size_off | offset_off | adj | seed |
| ---: | ---: | ---: | --- |
| 1024 | 1020 | -1508 | 0x116C4B46EACABA5 |
| 664 | 660 | +3476 | 0xD4C07427B74C818E |
| 964 | 960 | -6696 | 0xAFDAE7074F40F834 |
| 136 | 132 | +4304 | 0xA28BFC303CE665BA |
| 592 | 588 | -3984 | 0xFF3532DDAC34BA66 |
| 652 | 648 | -7080 | 0x1DFCEDD20A3EE02C |
| 4 | 0 | +2268 | 0x88942C9716431E06 |

### 验证闭环（真实加密文件 `samples/steam-2026-08-06/global-metadata.dat`）

- 布局自动判定：`offset_size_count`，87 三元组，score 0.744。
- 7/7 节段范围与解密通过；结构门：string 可打印 94.8%、stringLiteralData 96.2%
  （text），stringLiteral 单调率 1.0（index），其余 4 节 binary。
- 定位器 dump 的替换表（0x187356110，256 B）与 profile `substitution_table_hex`
  逐字节一致。
- 裁决 PASS。等价人工确认：表字节即 `metadata_probe.py` 使用的替换表。

## 五、踩坑记录（后续会话勿重踩）

1. `idaapi.segments()` 在 IDA 9.3 不存在 → 用 `ida_segment.get_first_seg/get_next_seg`。
2. IDA 会话内 `sys.modules` 缓存旧版本模块 → 重跑前 `sys.modules.pop(...)`。
3. `global_fanout` 原按逐指令 `XrefsFrom` 统计，400 函数 20+ 分钟未完成 → 改为
   反编译文本正则提取全局名 + `XrefsTo`，降至数分钟。
4. 拷贝正则前缀 `sub_[0-9A-Fa-f]{8}` 误匹配函数声明 `sub_18069C5E0()` 且 IDA
   函数名 hex 长度可达 9 位 → 改为直接匹配拷贝源表达式（`qword_<file> + *(_DWORD *)(qword_<hdr> + N) ± adj`），
   该形态仅拷贝调用独有。
5. 正则分支顺序：`(\d+|0x...)` 会抢先匹配 `0x2F4u` 的 `0` → hex 分支放前。
6. 定位器输出 JSON 曾剥掉 `table_hex`，验证闭环缺表字节 → 保留。
7. MCP 长任务请求超时属预期：脚本在 IDA 后台线程继续，靠 `progress.txt`/
   输出文件轮询确认完成（`out/locator-08-06/`）。

## 六、产物与证据位置

- 代码：本仓库 `tools/`、`metadata_locator_plugin.py`、`tests/`。
- 运行输出（gitignored，可再生）：`out/locator-08-06/`（locate_candidates.*、
  decompile_rank*.c）、`out/candidate_profile_08_06.json`（全自动提取的候选 profile，
  含 table_hex）、`out/verify-08-06-real.*`。
- 参考：主工作区 `profiles/steam-2026-08-06.json`、`samples/steam-2026-08-06/`。

## 七、会话中 IDA 实例变更

- 旧实例（pid 26828）因卡死被终止；新实例（pid 18380，端口 13337）重新打开
  08-06 IDB，定位器运行完毕后实例保持打开。
- 定位器为只读分析，未对 IDB 做任何重命名/类型/注释修改，无需保存 IDB。

## 八、后续工作

1. 按 `docs/DESIGN_SECTION_SOLVER.md` 实现 `tools/solve_section_map.py`（31 段映射
   自动求解），验收：映射与 08-06 profile 逐项一致、重建 SHA-256
   `73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7`。
2. 把 `candidate_profile → --apply` 提升流程接入新 profile 生成。
3. 定位器裁决门、提取器正则的健壮性在下一个真实版本上验证（预期需要小调）。
