# 2026-08-20：新版本（08-20 更新）恢复会话日志

## 报告目的

08-20 游戏更新（第 5 个加密版本），用 universal v2 流水线恢复新 metadata。
记录归档、管线结果、solve 根因分析（已完成）与最终结果。

## 一、样本与归档

- 游戏路径：`C:\Program Files (x86)\Steam\steamapps\common\Limbus Company`
- metadata：`LimbusCompany_Data\il2cpp_data\Metadata\global-metadata.dat`
- 归档至 `samples/steam-2026-08-20/`：

| 文件 | 大小 | SHA-256 |
| --- | --- | --- |
| GameAssembly.dll | 139,981,824 | 815F5EE3461F22C2C3ECCF4C9E0FBED8C4E21E7A296D16AE39849C7202DD5DD4 |
| global-metadata.dat | 43,756,016 | 89C223F22F9B6E2469FA23B8034E88760044E7E75A5DAFE334FF8EC5726783DB |
| LimbusCompany.exe | 901,704 | 3AA5B3836DB3AB8B37C53CE12D56172150EEAA81D115292517800BCCCE7FE37E |
| UnityPlayer.dll | 36,195,240 | 9C13F173D3BAB3AEF5589C6D38BADEEAD7A7AE547A2A531268FD0DA9888CCE53 |

## 二、管线结果（`python -m universal.pipeline ... --name steam-2026-08-20`）

| 阶段 | 结果 |
| --- | --- |
| locate | PASS，top1=6449386160（score 156.2，唯一候选） |
| extract | PASS，header 1476 B / 123 三元组，layout=`count_size_offset`，seed `0xA74F5816B712C7B8`，table@`0x187372860`，7 节 |
| verify | PASS（score 0.715，7/7 节解密过结构门） |
| solve | **FAIL**（修复前）：`SolveError "无可行锚点槽位组合"`（solve_versioned.py:364） |
| solve | **PASS**（修复后）：31 节全映射，review 空 |
| rebuild | **PASS**：43,751,969 B，5 门自验证全过 |

### extract 的 7 个受保护节（锚点）

| entry | size_off | offset_off | adj | seed | phys | size |
| --- | --- | --- | --- | --- | --- | --- |
| 13 | 160 | 164 | +1784 | 0x5E25C0ED52C8149A | 0x848 | 113404 |
| 48 | 580 | 584 | -2356 | 0x207A9B033C9F09C3 | 0x1c344 | 798632 |
| 85 | 1024 | 1028 | -2292 | 0xE92C6F83B7B263FF | 0xdf2ec | 4786474 |
| 22 | 268 | 272 | +6956 | 0x27DB28E47BBBDB06 | 0x571e80 | 846060 |
| 115 | 1384 | 1388 | -1288 | 0x5B0DA23B03F7F301 | 0x64076c | 9188320 |
| 62 | 748 | 752 | -1700 | 0xE8129F072824612F | 0x15f3d84 | 2095596 |
| 101 | 1216 | 1220 | -2336 | 0xB7E7B972EC201CB6 | 0x272ef4c | 10608 |

文件总大小 0x29ba9f0 = 43,756,016。

## 三、solve 失败根因分析（已完成）

### 3.1 链式物理布局成立（31 节全部验证）

锚点物理链 + 锚点间非保护节（规范序平铺）精确吻合，**31 个 section 的 header
offset 字段与物理位置差全部 ≤ 7,163（MAX_ADJ=0x8000）**：

- **gap3**（string→properties，8810 B）= events(entry54, 8808) + 2 pad ✓
- **gap5**（methods→fields，7,275,064 B）= 4×rec12（46=127,368、91=162,168、104=560,184、107=4,074,708）+ rec1（15=2,350,635）= 7,275,063 + **P=1** ✓
- **gap6**（fields→assemblies，15,972,316 B）= 固定 3,990,580（genericParameters=34、genericContainers=36、typeDefinitions=77、images=31）+ rec4=[35,64,65,83] + rec8=[82] = 11,981,736 + **P=0** ✓
- **gap8**（assemblies→EOF，2,658,612 B）= fieldRefs(106, 11,712) + referencedAssemblies(21, 3,672) + attributeData(11, 1,774,464) + attributeDataRange(81, 683,928) + uvcpTypes(59, 102,104) + uvcpRanges(45, 67,368) + exportedTypeDefinitions(79, 13,060) = 2,656,308 + 尾部冗余 2,304 B（与 08-06 尾部 4,928 B 同类，非矛盾）✓

### 3.2 08-20 的 offset 字段语义**未变**：仍是物理位置近似

- 早期"offset = 逻辑布局位置、差异达数 MB"的结论**错误**（entry107 误用了
  gap5 起点 0xf03b4c 而非链式位置 0x12110af 对比）。
- 逐节验证：entry107 offset=18,937,012 vs 物理 18,944,175，**差 7,163**；
  entry79 offset=43,743,564 vs 物理 43,740,652，差 -2,912；全部 31 节 ≤ 8,000。
- **真正根因**：solve pool 构建的越界过滤
  `if e["offset"] + e["size"] > len(metadata) + 4: continue`
  把 entry79（exportedTypeDefinitions）误删——其 offset 偏大 2,912 导致
  offset+size = 43,756,624 > 文件 43,756,016（越界 608 B），但物理位置
  43,740,652+13,060 = 43,753,712 < EOF 完全合法。链尾节被删 → 无可行组合。
- 08-06/08-13 未触发：其尾部节 offset 偏小（未越界）。

### 3.3 其他验证结论

- fingerprint/3-probe 循环论证：从 logical 处取内容必然在该处命中，不能证明"非保护节物理=logical"；08-20 实际布局是受保护锚点 + 非保护节链式平铺。
- examine_gaps：gap5 内容呈 12B 记录（如 `4e 00 00 00 bc 99 00 00 86 00 00 00`），与 rec12 结构一致。
- attributeDataRange 记录内容与 08-06 逐字节同构（`{0x02000002,0},{0x02000003,8},...`），startOffset 呈 TypeDef/Field/MethodDef token 模式（0x02/0x04/0x06 高字节），非文件偏移，但为合法数据（08-06 已 solve 同构）。
- 版本历史：07-30 (756B/63)、08-06 (1044B/87)、08-13 (1236B/103)、08-20 (1476B/123)。

## 四、修复（已完成）

1. **pool 越界过滤**：`len(metadata) + 4` → `len(metadata) + MAX_ADJ`（容忍 header
   offset 漂移 ≤ 0x8000；entry79 保留，entry0/27/90 等真幻影仍被滤除）。
2. 其余逻辑（rec 匹配 + 链式 padding + 位置近似 + 内容签名）无需改动——31 节
   位置近似全部满足 |phys - logical| ≤ MAX_ADJ。
3. 重跑 pipeline 全绿：solve PASS、rebuild PASS（5 门自验证全过，
   sanity `0xFAB11BAF`、version 39、stringLiteral dataIndex 单调、rec 全部一致）。

### 产物

- `out/solve-08-20/steam-standard.dat`（43,751,969 B）
- `out/solve-08-20/steam-profile.json`（31 节映射 + entries + anchor_slots）
- 与 08-06 逐节 size 对比全部合理增长（vtableMethods +47,072、methods +11,200、
  typeDefinitions +5,084、string +5,085 等；零尺寸节保持 0）

## 五、调试脚本（Temp 目录）

`debug_solve_0820.py`、`probe_0820.py`、`trace_solve_0820.py`、`check_fill_0820.py`、
`examine_gaps.py`、`fingerprint_check.py`、`layout_hypothesis.py`、`gap_enum.py`、
`chain_check.py`、`offset_vs_chain.py`、`entry_dump.py`、`verify_all_adj.py`。

## 六、待办/可选

- attributeDataRange 的 startOffset token 语义（0x02/0x04/0x06 高字节）可用 IDA
  确认消费代码（不阻塞 solve）。
- 08-20 首启验证 + Il2CppDumper 导出（同 08-06 流程，见 `docs/REBUILD_GUIDE.md`）。