# 31 段映射求解器设计文档

> **实现状态：已实现（2026-08-08）**。`tools/solve_section_map.py` 落地，08-06 端到端
> 验收通过：31 节映射与 profile 逐项一致、重建 SHA-256 精确命中
> `73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7`、
> `requires_review == 0`。回归入口：`tests/run_solver_regression.py`。

本文是"自动恢复 metadata 解密参数"流水线的下一阶段设计：给定解密后的自定义 header
（N 个三元组）与解密参数（header seed/替换表/7 个受保护节段 seed），**自动把 31 个
真实 section 映射到标准 v39 metadata 字段，并闭合物理偏移修正（adj）**。

当前阶段已交付：定位器（`locate_metadata_init.py`）、提取器
（`extract_decrypt_params.py`）、验证闭环（`candidate_verify.py`）。本求解器完成后，
慢路径（算法/布局变化时的新版本恢复）即可全自动闭环。

## 1. 问题形式化

输入：

- 加密的 `global-metadata.dat`（文件大小 F）。
- 解密参数（来自提取器/验证闭环）：
  - `header_size` H、`header_seed`、替换表 256 字节；
  - 7 个受保护节段的 `{size_off, offset_off, adj, seed}`。
- 参考标准文件：旧版本 `global-metadata-standard-*.dat`（提供每个标准 section 的
  权威 `(offset, size, count)` 与字节内容锚点）。

中间量：

- 解密 header 得 N 个三元组 `E_i = (o_i, s_i, c_i)`（布局已由 `candidate_verify.py`
  自动判定：`(offset,size,count)` 或 `(size,count,offset)`）。
- 标准 v39 共 31 个 section，名字集合 `S`（stringLiteral … windowsRuntimeStrings）。

输出（即新 profile 的 `standard_sections`）：

- 每个 section：`custom_entry_index`（三元组下标）与 `physical_offset_adjustment`。

## 2. 约束目录（全部可机械判定）

| # | 约束 | 依据 | 强度 |
| --- | --- | --- | --- |
| C1 | `s_i = c_i × rec_size[s]`（或 `s_i == 0` 的零尺寸表） | 自定义 header 保留真实 size/count；`rec_size[s]` 从参考标准文件 header 直接推导 | **强**（整数整除，直接淘汰绝大多数诱饵） |
| C2 | 物理偏移 `o_i + adj_i ∈ [0, F]` 且 `o_i + adj_i + s_i ≤ F`（辅助表例外，见 08-06 index 7/23） | 文件范围 | 强 |
| C3 | 31 节物理上首尾相连成链：`end_i == start_{i+1}`，允许 ≤4 字节对齐 padding | 08-06 已验证链 | **强**（把排序问题变成近似线性方程） |
| C4 | `|adj_i| < 0x4000` | 实测最大 9948（08-06 windowsRuntimeTypeNames） | 中 |
| C5 | 非加密节与参考标准文件对应节的字节锚点（去重集 Jaccard 或前缀指纹） | 08-06：referencedAssemblies 1.000、uVCPRanges 1.000、genericParameters 0.921、fieldRefs 0.926 | 中（内容跨版本微变，需容差） |
| C6 | 受保护节用提取器 seed 解密后通过结构门（text/index/binary 分类 + 单调/可打印率） | `candidate_verify.py` 已实现 | 强（错误 seed 无法通过） |
| C7 | 受保护节在 header 中的槽位（`size_off`）与 C1 推导的条目一致 | 提取器 | 强（交叉校验） |

## 3. 四相算法

### 相 1：记录大小匹配（C1 + C7）

1. 从参考标准文件 header 读 31 个 `(size, count)` → `rec_size[s] = size / count`
   （count > 0；零尺寸表记特殊标记）。
2. 对每个三元组 `E_i`：候选节集合 `cand(i) = { s : s_i == 0 且 s 零尺寸 或 s_i % rec_size[s] == 0 且 s_i / rec_size[s] == c_i }`。
3. 构造二分图：`|E| × 31`，用 C1 剪枝后通常每个 `E_i` 只剩 1~3 个候选
   （同记录大小的节：4 字节记录的有 string/fieldRefs/referencedAssemblies 等）。
4. 对歧义解：非加密节用 C5 锚点打分，受保护节用 C6 槽位一致性（C7）打分；
   仍并列 → 留到相 3 用链唯一性消歧。

复杂度：O(N × 31)，N ≈ 87。

### 相 2：内容指纹定位（C5）——直接得出物理偏移与 adj

非加密节在磁盘上是明文（未受保护），可以直接在加密文件中**搜索其内容**：

1. 对每个非加密节，从参考标准文件取节首 64 字节作指纹（若指纹与前后节重叠，
   改用节内多个采样窗口，取最高匹配）。
2. 在新文件中扫描指纹：允许 ≤10% 字节漂移，取最长连续匹配窗口作为物理位置
   `p_s`。
3. `adj_s = p_s - o_s`（`o_s` 为 C1 匹配到的三元组 offset 字段）。
4. 若多命中（内容重复/空表），用 C3 链约束消歧。

08-06 经验：锚点相似度 0.814~1.000，节首指纹匹配应更稳；这是把 08-06 人工
"链式连续性"做法的机械化。

### 相 3：链装配（C2/C3/C4）——受保护节落入间隙

1. 已定位的非加密节按物理位置排序 → 骨架链；骨架间 gap = 待填充的受保护节
   （数量必须恰好 7 且每 gap 的字节数 ≈ 该节 size ± 4 padding）。
2. 对每个受保护节候选分配：gap 大小匹配 + C6 解密验证（用提取器 seed）。
3. 全链校验：C2 范围 + C4 adj 界 + 首节起始与文件头对齐合理性。
4. 输出 31 节 `(custom_entry_index, adj)` 完整映射表。

### 相 4：全量重建与外部验证

1. 按标准 v39 布局重建 metadata（复用主工作区 `metadata_probe.py` 的
   `rebuild_standard_metadata` 逻辑）。
2. 验证门：sanity `0xFAB11BAF`、version 39、31 节连续、stringLiteral 单调、
   真实字面量存在。
3. 外部验证：LibCpp2IL 独立解析 + 与新 `GameAssembly.dll` 联合初始化
   （`load_from_file=True`）。
4. 全部通过 → 写入新 profile（`--apply` 提升）。

## 4. 歧义与退化处理

| 场景 | 处理 |
| --- | --- |
| 同记录大小节多候选（4 字节组） | 相 2 内容指纹 + 相 3 链唯一性；仍歧义 → `requires_review` |
| 内容跨版本大改（C5 失效） | 指纹窗口缩短/多窗口投票；全失效 → 依赖链装配 + 相 4 验证 |
| 零尺寸表（windowsRuntimeStrings） | 相 1 特殊标记；物理位置取相邻节边界 |
| 辅助表越界（08-06 index 7/23 类） | C2 放行越界条目但不入 31 节映射 |
| 诱饵三元组合法外形 | C1 记录大小淘汰；残余用 C3 链长度约束排除 |
| 布局翻转（offset,size,count ↔ size,count,offset） | `candidate_verify.py` 已自动判定，求解器消费其结果 |

## 5. 失败阶梯（每级产出可解释报告）

1. 相 1 无解 → 提示记录大小表与参考标准版本不匹配（可能跨 Unity/metadata 版本）。
2. 相 2 全部指纹失败 → 非加密节内容可能也被改写；转相 3 全链搜索（gap 枚举）。
3. 相 3 链不闭合 → 枚举 gap 组合超限时报告 top 候选链 + 每节 C6 证据，交人工/LLM 审核。
4. 相 4 外部验证失败 → 保留重建文件 + 失败门日志，不写 profile。

## 6. 接口与组件

```
tools/solve_section_map.py        # 本设计实现（已交付，2026-08-08 验收 PASS）
  输入：candidate_profile.json（提取器）+ 加密 metadata + 参考标准文件
  输出：section_map.json（31 节映射）+ report.json/md
tools/metadata_probe.py           # 主工作区复用（重建/验证）
tools/candidate_verify.py         # 前置：布局判定（本仓库已交付）
```

数据流：

```
extract_decrypt_params.py ─┐
candidate_verify.py ────────┤→ solve_section_map.py → 相4 重建验证 → --apply → profiles/
参考标准文件 ───────────────┘
```

## 7. 验收标准（08-06 回归）

- 输出映射与 `profiles/steam-2026-08-06.json` 的 `standard_sections` 逐项一致
  （31 个 `custom_entry_index` + `physical_offset_adjustment` 全同）。
- 相 4 重建文件 SHA-256 == `73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7`。
- `requires_review == 0`。
