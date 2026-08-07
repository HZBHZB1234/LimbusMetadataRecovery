# 2026-08-08（第二段）：31 段映射求解器实现与 08-06 验收

## 报告目的

实现 `docs/DESIGN_SECTION_SOLVER.md`（四相算法）为 `tools/solve_section_map.py`，
并在 08-06 真实加密 metadata + 参考标准文件上完成设计文档第七节的全部验收判据。
衔接当日第一段存档（定位/提取/验证三件套 + 求解器设计）。

## 一、算法落地（与设计的对应）

| 设计 | 实现 |
| --- | --- |
| 相 1 C1 记录大小匹配 | `candidates_for(entry)`：rec_size 整除 + 同版本 size 精确匹配（blob 兜底）+ 零尺寸配对；结果去重 |
| 相 2 C5 内容指纹 | 节首 8 窗口×16B 锚点扫描 + 扩展窗口字节比对（≤10% 漂移，`MIN_RATIO=0.9`），锚点一致性分组取最优 |
| 相 3 C3 链装配 | 受保护节物理 = logical + extractor.adj；非加密节物理序必须规范序递增；全链 end==next_start（≤4 padding） |
| 相 4 重建验证 | 与主工作区 `metadata_probe.rebuild_standard_metadata` 同语义重建 v39 文件 → SHA-256 比对 |
| 零尺寸节 | snap：物理 = ≥ logical 的最小链边界（边界集 = 全部真实节 start/end），C4 \|adj\|<0x4000 校验 |

## 二、08-06 验收结果（全部 PASS）

- 22 个非加密节指纹定位 ratio=1.0（windows=8），物理位置与人工链逐项一致。
- 7 个受保护节由"指纹必然失败"识别（加密内容无法在文件中匹配）：
  stringLiteral/stringLiteralData/string/properties/methods/fields/assemblies ——
  与 extractor 的 7 个 seed 槽位完全吻合（C7 交叉验证）。
- 31 节映射与 `profiles/steam-2026-08-06.json` 逐项一致（custom_entry_index +
  physical_offset_adjustment 全同），含零尺寸节：windowsRuntimeTypeNames entry 5
  adj +9948（snap 到链尾 0x029A61FC）、windowsRuntimeStrings entry 57 adj +328
  （snap 到 0x029A2EF8）。
- 重建：43,667,903 B，SHA-256
  `73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7` 精确命中；
  `requires_review == 0`；裁决 PASS（44 项 gate 全过）。
- 报告：`out/solve-08-06-cli.json/md`；重建文件 `out/standard-rebuilt-08-06.dat`。

## 三、实现要点与坑（后续会话勿重踩）

1. **指纹失败 = 受保护信号**：加密节内容不可能匹配，`unlocated` 集合必须恰为
   受保护节数（07-30/08-06 均 7）。该门同时充当"参考文件版本匹配"检测。
2. **假阳性锚点**：assemblies 曾以 ratio 0.60 误命中（1/8 窗口随机撞上）——
   `MIN_RATIO=0.9` 拒绝，否则破坏 unlocated 集合与命名。
3. **C1 候选去重**：rec 匹配与 size 匹配会重复产出同名候选，命名逻辑
   `len(cands)==1` 需去重后判断。
4. **受保护节命名消歧**：rec 4 组（stringLiteral/fieldRefs/...）与 rec 12 组
   （fields/parameters/...）由链间隙规范序唯一化（候选名必须落在该节相邻
   非加密节之间）。
5. **u64 seed 不能进 JSON 数字**：以 hex 字符串存储，rebuild 时 `int(s,16)`。
6. **受保护节数校验**：`len(unlocated) != len(protected)` 时走 review，不静默。
7. **零尺寸 snap 的合理性**：文件证据不足以决定零尺寸节物理位置；snap 规则
   （最小边界 ≥ logical）精确复现人工 profile 的两个 adj（328/9948），C4 校验
   兜底。若未来版本不满足，进入 requires_review 而非硬失败。

## 四、apply 提升闭环（同日追加）

- `tools/apply_profile.py`：candidate_profile + section-map → 正式 profile
  （header/substitution_table_hex/protected_sections/standard_sections/
  metadata_size/metadata_sha256，`identified_as` 由结构门自动分类）。
- 自检：用生成 profile 重建 v39 → SHA 精确命中 `73194A...57A2E7`。
- 关键验证：主工作区 `tools/metadata_probe.py`（规范消费者）直接读取生成
  profile → 重建 43,667,903 B、SHA 命中、31 节、零告警。
- `solve_section_map.py` 增加独立 `*-section-map.json` 产物（apply 的输入）。
- 修复：`decrypt_header` 返回布局名（字符串），`list()` 拆字符 → 用
  `LAYOUTS[layout_name]`；`classify_section` 返回元组需取 kind。

## 五、遗留（后续工作）

1. 跨版本参考验证：用 07-30 标准文件作参考解 08-06（验证 C5 漂移容差与 blob
   size 匹配失效时的退化路径）；下个真实版本验证定位门/提取正则。
2. 定位器/提取器/求解器的健壮性在下个真实版本（09-xx）上验证，预期需要小调。
