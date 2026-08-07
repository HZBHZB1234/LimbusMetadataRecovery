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
| 映射求解器 | `tools/solve_section_map.py` | 31 段映射自动求解：C1 记录大小 + C5 内容指纹 + C3 链装配 + 相 4 重建验证 |
| 求解器设计 | `docs/DESIGN_SECTION_SOLVER.md` | 31 段映射求解器设计文档（已实现，验收见下） |

## 回归结果（08-06 真实 IDB，端到端）

| 阶段 | 结果 |
| --- | --- |
| 定位器 | top-1 = `sub_18069C5E0`（真值 init）；score 161.0，fanout 330 |
| 提取器 | header_size 1044、header_seed `0xBC41EAFC33962B00`、表 `0x187356110`、7 节参数与 `profiles/steam-2026-08-06.json` 逐项一致（66 项夹具断言全过） |
| 验证闭环 | 布局自动判定 `offset_size_count`（87 三元组）；7/7 节段解密通过结构门（string 94.8%、stringLiteralData 96.2% 可打印，stringLiteral 单调 1.0）；裁决 **PASS** |
| 映射求解器 | 22 非加密节指纹定位 ratio=1.0；7 加密节由"指纹必然失败"识别 + extractor 参数；零尺寸节 snap 链边界；**31 节映射与 profile 逐项一致**（entry+adj 全同），重建 SHA-256 == `73194A...57A2E7`，`requires_review == 0`，裁决 **PASS** |

07-30 提取器夹具（`tests/fixtures/metadata_initialize_current.c`）33 项断言全过。

## 求解器验收（DESIGN_SECTION_SOLVER.md 第七节）

```powershell
python tests\run_solver_regression.py        # 全自动验收：映射全同 + 哈希比对
python tools\solve_section_map.py `
  --metadata E:\desktop\work\LimbusDecompile\samples\steam-2026-08-06\global-metadata.dat `
  --profile out\candidate_profile_08_06.json `
  --reference E:\desktop\work\LimbusDecompile\analysis\global-metadata-standard-steam-2026-08-06.dat `
  --expect-sha256 73194A637E4BEF48F5D0396158F2CFEEAC484EFF4864AE01F6CDAE603057A2E7 `
  --rebuild-output out\standard-rebuilt-08-06.dat
```

关键判据：`requires_review == 0` + 重建 SHA-256 精确命中（43,667,903 B）。

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
solve_section_map.py → section_map.json + 标准 v39 重建文件
        ↓
（审核后 --apply 提升为正式 profile）
```

每个步骤都产出机器可读 JSON 与人类/LLM 可读 Markdown 报告；需要人工判断的歧义项进入 `requires_review` 清单，不静默失败。
