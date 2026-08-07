# Limbus Metadata Recovery

《边狱公司》(Limbus Company) Steam 版 IL2CPP metadata 解密的**自动定位与参数恢复**子项目。

独立于主工作区 `LimbusDecompile`，只包含与"解密入口定位 → 参数提取 → 候选验证 → 31 段映射求解"相关的代码与设计文档。大型样本、IDB、导出产物仍在主工作区归档，不进入本仓库。

## 背景

- 磁盘 `global-metadata.dat` 是加密的：自定义 header（07-30 为 756 B/63 三元组，08-06 为 1044 B/87 三元组）+ 7 个受保护 section。
- 解密算法：`xorshift64(13,7,17)` + 256 字节替换表逐字节 XOR，各区域独立 seed。
- 旧 `metadata_trace.py`（IDA 插件）用"首个字符串引用 → 首个调用者"定位解密入口，依赖枚举顺序，跨版本脆弱（详见主工作区 `docs/FINDINGS.md` F-0004）。
- 本仓库实现证据驱动的候选评分定位、全自动参数提取、候选验证闭环，并给出 31 段映射求解器设计。

## 组件

| 组件 | 文件 | 说明 |
| --- | --- | --- |
| 报告框架 | `tools/report.py` | 统一产出 `report.json` + `report.md`，`requires_review` 门 |
| 定位器 | `tools/locate_metadata_init.py` | IDA 侧候选评分（xorshift 扫描 + 反编译特征），MCP/插件双入口 |
| 提取器 | `tools/extract_decrypt_params.py` | 反编译文本正则提取 header/seed/table/section 参数 |
| 验证闭环 | `tools/candidate_verify.py` | 参数级验证：布局判定、节段解密、结构门 |
| 求解器设计 | `docs/DESIGN_SECTION_SOLVER.md` | 31 段映射求解器设计文档（实现为后续阶段） |

## 参考基线

- 08-06 构建真值：init `sub_18069C5E0`、map `sub_180693580`、替换表 RVA `0x7354910`（IDB：主工作区 `samples/steam-2026-08-06/GameAssembly.dll.i64`）。
- profile：主工作区 `profiles/steam-2026-08-06.json`。
- 07-30 反编译夹具：`tests/fixtures/metadata_initialize_current.c`（来自主工作区 `analysis/ida/`，用于提取器 TDD）。

## 流程

```
locate_metadata_init.py → locate_candidates.json
        ↓
extract_decrypt_params.py → candidate_profile.json
        ↓
candidate_verify.py → 裁决 PASS / PASS_WITH_REVIEW / FAIL + report
        ↓
（审核后 --apply 提升为正式 profile）
```

每个步骤都产出机器可读 JSON 与人类/LLM 可读 Markdown 报告；需要人工判断的歧义项进入 `requires_review` 清单，不静默失败。
