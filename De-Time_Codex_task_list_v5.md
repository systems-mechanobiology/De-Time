# De-Time Codex 可执行任务清单（2026-04-08）

> 目标：把当前仓库推进到  
> 1）JMLR MLOSS 可重投；  
> 2）agent-native v1；  
> 3）与 benchmark / Dec-SR 主线一致。  
>  
> 说明：每个任务都按「目的 / 需要修改的文件 / 具体动作 / 完成标准」给出。  
> 默认先做 Wave 1–3，再做 Wave 4–5。

---

## Wave 1 — 先把 release 做真

## Task 1.1 — 完成首个正式 release

**目的**  
把“review snapshot”变成可安装、可引用的软件版本。

**修改文件**
- `pyproject.toml`
- `PUBLISHING.md`
- `README.md`
- `.github/workflows/wheels.yml`
- `CHANGELOG.md`
- `docs/install.md`
- `docs/citation.md`

**动作**
1. 确认 `project.name = "de-time"` 保持不变。
2. 创建发布 tag 方案：`de-time-v0.1.0`。
3. 校验 wheels workflow 在 tag/release 上发布 PyPI。
4. 在 PyPI 真正创建 `de-time` 项目并完成 trusted publishing。
5. 发布 GitHub release。
6. 更新 README/install 文案，把 “reviewed snapshot” 改成正式 release 语气。
7. 在 docs/citation 中加入版本化引用方式。

**完成标准**
- `pip install de-time` 可用
- GitHub Releases 非空
- GitHub Tags 非空
- README/install 文档不再默认 GitHub URL 安装

---

## Task 1.2 — 发布后 smoke test matrix

**目的**  
确保 release 不是“能构建，不能用”。

**修改文件**
- 新建 `scripts/release_smoke_matrix.py`
- `.github/workflows/wheels.yml`
- `docs/reproducibility.md`

**动作**
1. 对以下场景做 smoke test：
   - `import detime`
   - `import tsdecomp`
   - `python -m detime version`
   - `python -m tsdecomp version`
   - one Python call
   - one CLI `detime run`
2. 记录 OS / Python version / wheel source。
3. 将 smoke test 脚本加入 release pipeline。
4. 文档化 release verification 步骤。

**完成标准**
- release workflow 自动执行 smoke matrix
- 失败会阻断发布

---

## Wave 2 — 统一 reviewer-facing 文档

## Task 2.1 — 重写 `JMLR_MLOSS_CHECKLIST.md`

**目的**  
消除旧 `tsdecomp` 身份与旧方法边界。

**修改文件**
- `JMLR_MLOSS_CHECKLIST.md`

**动作**
1. 将标题改为 `De-Time`。
2. 删除把 `DR_TS_REG` 列为 core method 的表述。
3. 明确：
   - canonical package = `detime`
   - `tsdecomp` = compatibility alias
   - flagship = `SSA`, `STD`, `STDR`, `MSSA`
4. 明确 active user community 仍需补证据。
5. 与 `JMLR_SUBMISSION_CHECKLIST.md` 的措辞对齐。

**完成标准**
- 文件内不再出现与 README/PUBLISHING 冲突的 scope 语句

---

## Task 2.2 — 重写 `JMLR_SOFTWARE_IMPROVEMENTS.md`

**目的**  
让“软件改进说明”与当前包边界一致。

**修改文件**
- `JMLR_SOFTWARE_IMPROVEMENTS.md`

**动作**
1. 删除 `DR_TS_REG` retained native path 叙述。
2. 重新写成以下结构：
   - package extraction
   - stable API/CLI
   - native acceleration for retained flagship methods
   - multivariate support
   - packaging/release engineering
   - docs/examples/CI
   - remaining limitations
3. 说明 benchmark-derived methods 已迁出。
4. 说明比较页已补 `PySDKit` / `SSALib` / `sktime`。

**完成标准**
- reviewer 读完该文件后不会再怀疑你仍在主包中保留 benchmark-derived methods

---

## Task 2.3 — 统一 `README` / `PUBLISHING` / `docs/install`

**目的**  
保证任何入口看到的 install/release/compatibility story 完全一致。

**修改文件**
- `README.md`
- `PUBLISHING.md`
- `docs/install.md`
- `docs/migration.md`

**动作**
1. 对齐以下事实：
   - product brand
   - distribution name
   - preferred import
   - legacy import
   - compatibility scope
2. 若 PyPI 已上线，更新 install 命令。
3. 在 migration guide 中给出：
   - `tsdecomp` → `detime` 对照表
   - deprecated imports
   - removal timeline

**完成标准**
- 四份文档对 install/release/compatibility 的描述一字不冲突

---

## Wave 3 — 把 benchmark residue 真正移出主包叙事

## Task 3.1 — 清理 `docs/examples.md`

**目的**  
移除残余 benchmark 引导。

**修改文件**
- `docs/examples.md`

**动作**
1. 删除 `visual_leaderboard_walkthrough.py`
2. 删除 “Benchmark heatmap walkthrough”
3. 删除对 `tutorials/visual-benchmark.md` 的链接
4. 保留：
   - univariate quickstart
   - multivariate MSSA
   - method survey
   - profile and CLI
   - visual univariate / comparison / multivariate
5. 如果要保留 benchmark example，明确写：
   - “belongs to companion benchmark repo”

**完成标准**
- examples 页面只展示主包可辩护功能

---

## Task 3.2 — 清点 `examples/` 目录并移动 benchmark 脚本

**目的**  
让 examples 目录只包含主包示例。

**修改文件**
- `examples/`
- 可能新增 `de-time-bench/examples/`

**动作**
1. 遍历 examples 脚本
2. 标记为：
   - keep in De-Time
   - move to benchmark repo
3. 将 benchmark/leaderboard/heatmap 类脚本迁移
4. 更新 docs 中的路径与截图引用

**完成标准**
- `examples/` 目录中不再出现与主包定位冲突的脚本

---

## Task 3.3 — companion benchmark repo 落地

**目的**  
把 README 中声称存在的 `de-time-bench` 变成可核验对象。

**修改文件**
- `README.md`
- `docs/comparisons.md`
- `docs/reproducibility.md`
- benchmark companion repo 自身

**动作**
1. 创建/公开 `de-time-bench`
2. 在 README 中加入明确 URL
3. 在主包 docs 中加入一段 boundary 说明：
   - De-Time = reusable decomposition software
   - de-time-bench = benchmark orchestration and capability maps
4. companion repo 至少包含：
   - benchmark scope README
   - installation
   - relation to De-Time
   - results reproduction path

**完成标准**
- reviewer 能够实际点击 companion repo
- 主包和 benchmark repo 的责任边界明确

---

## Wave 4 — 强化 JMLR 证据链

## Task 4.1 — 升级 `docs/comparisons.md` 为审稿级矩阵

**目的**  
让 comparisons 页不只像 narrative，而像 software evidence。

**修改文件**
- `docs/comparisons.md`

**动作**
1. 新增表格轴：
   - common result model
   - common config model
   - batch CLI
   - profiling path
   - multivariate support
   - native path
   - maturity labeling
   - release/publication state
2. 维持当前对手：
   - `statsmodels`
   - `PyEMD`
   - `PyWavelets`
   - `PySDKit`
   - `SSALib`
   - `sktime`
3. 删除一切可能被理解为“我们在每个方向都更强”的措辞。
4. 强调 De-Time 的优势只在：
   - workflow-oriented layer
   - common contract
   - selected native-backed flagship paths

**完成标准**
- comparisons 页面可以直接成为 JMLR paper 的 related software 素材

---

## Task 4.2 — 新增系统化 performance evidence

**目的**  
把单点 speedup 变成可复现的软件性能证据。

**修改文件**
- 新建 `docs/performance.md`
- 新建 `scripts/build_perf_snapshot.py`
- 新建 `examples/perf_inputs/`（如需要）
- `docs/comparisons.md`

**动作**
1. 为 retained flagship methods 建基准脚本：
   - `SSA`
   - `STD`
   - `STDR`
2. 固定：
   - input lengths
   - repetitions
   - platform metadata
   - backend used
3. 输出 markdown + csv/json summary
4. 在 docs 中引用该 snapshot
5. 可选：
   - 额外对位 compare upstream implementation where fair

**完成标准**
- 有一份可以由 Codex 一键重建的性能快照
- docs 中明确这是 software validation，不是 universal benchmark claim

---

## Task 4.3 — coverage story 透明化

**目的**  
避免 reviewer 误解 91.40% 是 whole-package coverage。

**修改文件**
- `README.md`
- `docs/reproducibility.md`
- 可能新增 `docs/testing.md`

**动作**
1. 明确表述：
   - current gate covers core-plus-flagship `detime` surface
2. 列出被 omit 的主要类别：
   - compatibility alias
   - CLI
   - viz / I/O
   - some wrappers
3. 解释原因：
   - 它们不是当前最强主张的中心层
4. 在 docs 中公开 `fail_under = 90`

**完成标准**
- reviewer 不会再因为 coverage wording 产生“偷换口径”的疑虑

---

## Task 4.4 — 补 adoption/community 最小证据包

**目的**  
尽量缓解 JMLR 对 active user community 的质疑。

**修改文件**
- GitHub issue templates
- README badges / links
- `JMLR_SUBMISSION_CHECKLIST.md`
- cover letter 草稿（若在 repo）
- `CONTRIBUTING.md`

**动作**
1. 开启 Discussions 或使用 issue templates
2. 至少创建几类真实 issue：
   - bug
   - enhancement
   - docs clarification
3. 若发布到 PyPI，记录下载数据
4. 若有外部试用者，征得同意后在 cover letter 作为 early adoption evidence
5. 在 CONTRIBUTING 中降低外部贡献门槛

**完成标准**
- cover letter 不再只能写“community is still early”而没有任何 supporting evidence

---

## Wave 5 — 升级成 agent-native / token-aware v1

## Task 5.1 — 补 JSON Schema

**目的**  
让 De-Time 的输入输出真正 machine-readable。

**修改文件**
- 新建 `schemas/decomposition-config.schema.json`
- 新建 `schemas/decomp-result.schema.json`
- 新建 `schemas/decomp-meta.schema.json`
- `docs/api.md`
- `AGENT_MANIFEST.json`

**动作**
1. 为 `DecompositionConfig` 生成稳定 schema
2. 为 `DecompResult` 生成稳定 schema
3. 为 `*_meta.json` 定义固定字段
4. 在 docs/api.md 中加入 schema section
5. 在 AGENT_MANIFEST 中加入 schema version 引用

**完成标准**
- 下游 agent 不需要阅读大段 prose，也能消费 config/result/meta

---

## Task 5.2 — 增加 summary/meta-only 输出模式

**目的**  
降低 agent 调用的 token 与 I/O 成本。

**修改文件**
- `src/detime/cli.py`
- `src/detime/io.py`
- `src/detime/core.py`
- `docs/api.md`
- `docs/quickstart.md`

**动作**
1. 新增 CLI 参数：
   - `--emit meta`
   - `--emit summary`
   - `--emit full`
2. 新增字段裁剪：
   - `--fields trend,season`
   - `--top-k-components`
3. 定义 summary 输出：
   - method
   - backend_used
   - result_layout
   - n_channels
   - component count
   - warnings
4. 保证 summary 是稳定 JSON

**完成标准**
- agent 可以只拿到小而稳定的 JSON，而不是巨大数组

---

## Task 5.3 — 增加 method recommender

**目的**  
把“Choose a Method”从静态文档升级为机器可调用能力。

**修改文件**
- 新建 `src/detime/recommend.py`
- `src/detime/cli.py`
- `docs/choose-a-method.md`
- `AGENT_MANIFEST.json`

**动作**
1. 设计一个 lightweight recommender：
   - input dimension
   - known period?
   - multivariate?
   - adaptive / non-stationary oscillations?
   - need speed or exactness?
2. 输出：
   - recommended methods
   - why
   - warning flags
3. CLI 增加：
   - `detime recommend-method ...`

**完成标准**
- agent 与新用户都可以先推荐，再运行，而不是先读大篇 docs

---

## Task 5.4 — 实现最小 MCP server

**目的**  
从自定义 agent docs 升级到标准 agent protocol。

**修改文件**
- 新建 `mcp_server/` 或 `src/detime_mcp/`
- 新建 `docs/mcp.md`
- `AGENT_MANIFEST.json`
- release docs

**动作**
1. 暴露最小工具集：
   - `recommend_method`
   - `decompose_univariate`
   - `decompose_multivariate`
   - `profile_method`
   - `get_result_schema`
2. 给每个工具定义严格 schema
3. 增加 toolset slicing：
   - `core`
   - `multivar`
   - `profiling`
4. 文档中说明如何接入 MCP registry

**完成标准**
- De-Time 能被标准 agent runtime 原生发现与调用
- 工具数少而精，不做一堆重复工具

---

## Wave 6 — 与 benchmark / Dec-SR 主线对齐

## Task 6.1 — 为 downstream scientific discovery 做 handoff contract

**目的**  
让 De-Time 可以自然成为 benchmark 与 Dec-SR 的前端。

**修改文件**
- 新建 `docs/ml-workflows.md` 补充 section
- 新建 `examples/ml/`
- 可能新建 `src/detime/handoff.py`

**动作**
1. 定义统一导出：
   - trend component for downstream SR
   - seasonal component + proposed frequency metadata
   - residual diagnostics
2. 给出示例：
   - De-Time → PySR
   - De-Time → ND2
3. 说明何时 decomposition fidelity 不足，不应继续 downstream discovery

**完成标准**
- 软件 story 不再只停留在 decomposition plotting，而能直接连到结构发现

---

## Task 6.2 — 方法 failure diagnostics 初版

**目的**  
把 benchmark 稿子的 failure-mode insight 反哺回软件。

**修改文件**
- 新建 `src/detime/diagnostics.py`
- `docs/reproducibility.md`
- `docs/choose-a-method.md`

**动作**
1. 增加基础 diagnostics：
   - likely fixed-period mismatch
   - possible phase instability
   - component leakage heuristic
   - multivariate channel imbalance
2. 输出到 `*_meta.json`
3. 在 CLI `summary` 模式中显示 warning flags

**完成标准**
- 软件开始具备“不是只给结果，还解释风险”的能力

---

## 最终执行顺序（强制）

1. **Wave 1**
2. **Wave 2**
3. **Wave 3**
4. **Wave 4**
5. **Wave 5**
6. **Wave 6**

---

## 完成后应达到的最终状态

- 可正式安装、可引用、可复现
- 软件身份、构建规则、reviewer 文档完全一致
- 主网页不再泄漏 benchmark residue
- 相关软件比较足够正面且有证据
- agent 可以低 token 成本调用
- De-Time 成为 benchmark 与 Dec-SR 主线的真正基础设施层
