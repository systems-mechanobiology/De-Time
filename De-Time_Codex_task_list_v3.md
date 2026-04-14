# De-Time Codex Task List（JMLR MLOSS v3）

> 目标：把当前仓库从“包装得比较认真的 benchmark extraction”推进到“边界清楚、可供 JMLR MLOSS review 的 standalone software”。  
> 执行原则：**先 package identity，再 public docs，再 release/package hygiene，再 evidence/paper**。  
> 下面每个任务都按“目标 / 具体修改 / 文件 / 完成标准”写，方便直接丢给 Codex 或分配给不同人。

---

## Wave 1 — Canonical software identity（最高优先级）

### T01. 让 `detime` 成为真实实现主体
**目标**  
把 `detime` 从 re-export shim 变成 canonical implementation namespace。

**具体修改**
- 将 `src/tsdecomp/` 中真实实现迁移到 `src/detime/`
- `src/detime/__init__.py` 不再写 compatibility-first shim narrative
- `src/detime/core.py`, `registry.py`, `cli.py`, `backends.py`, `io.py`, `profile.py` 不再 `from tsdecomp ...`
- 保留 `src/tsdecomp/` 仅作为最薄 alias（或另开 compat 包）

**重点文件**
- `src/detime/*.py`
- `src/tsdecomp/*.py`

**完成标准**
- 在 `src/detime/` 中执行全文搜索，不再出现 `from tsdecomp`
- `python -c "import detime; print(detime.__file__)"` 对应真实实现
- `tsdecomp` 只用于兼容，不再作为 equally-first-class identity

---

### T02. 重写 compatibility 策略
**目标**  
让 `tsdecomp` 成为 one-way compatibility story，而不是双主体并存。

**具体修改**
- 新增 `docs/migration.md`
- 将 README / quickstart / install / API 中所有主路径统一为 `detime`
- `tsdecomp` 只在 migration / compatibility 页面解释
- `PUBLISHING.md` 改写为：`detime` is canonical; `tsdecomp` is a legacy alias

**重点文件**
- `README.md`
- `docs/quickstart.md`
- `docs/install.md`
- `docs/api.md`
- `docs/project-status.md`
- `PUBLISHING.md`
- `ENTRYPOINTS.md`
- 新增 `docs/migration.md`

**完成标准**
- public docs 首屏不再把 `tsdecomp` 与 `detime` 并列展示
- `tsdecomp` 只出现在 migration / compatibility context

---

### T03. 修正 reviewer-facing 命名残留
**目标**  
消除 “for `tsdecomp`” 之类会让 reviewer 不爽的残留。

**具体修改**
- `JMLR_MLOSS_CHECKLIST.md`、`JMLR_SOFTWARE_IMPROVEMENTS.md`、其他 submission-facing 文件全部改成 `De-Time` / `detime`
- 检查 root 和 docs 中所有 `tsdecomp` 残留表述

**重点文件**
- `JMLR_MLOSS_CHECKLIST.md`
- `JMLR_SOFTWARE_IMPROVEMENTS.md`
- `submission/*`
- 全仓库 grep

**完成标准**
- reviewer-facing 文件不再把 `tsdecomp` 当 package 主体

---

## Wave 2 — 清理 public website / docs surface

### T04. 从公开导航移除 benchmark / agent 页面
**目标**  
让 docs 首页看起来像 library website，而不是 artifact portal。

**具体修改**
- 从 `mkdocs.yml` 主导航移除：
  - `Visual Benchmark Heatmaps`
  - `Agent Tools`
- 如果这些页面必须保留：
  - 移到 `docs/internal/`
  - 或不纳入 GitHub Pages 主导航

**重点文件**
- `mkdocs.yml`

**完成标准**
- 公共导航不再出现 `benchmark`, `leaderboard`, `agent`

---

### T05. 收紧 public API 文档
**目标**  
API 页面只展示真正支持的 public surface。

**具体修改**
- `docs/api.md` 仅保留：
  - `run`
  - `batch`
  - `profile`
  - Python public imports
- 移除或内迁：
  - `eval`
  - `validate`
  - `run_leaderboard`
  - `merge_results`

**重点文件**
- `docs/api.md`

**完成标准**
- API 页面不再暴露 benchmark orchestration commands

---

### T06. 下线公开 leaderboard tutorial
**目标**  
切断 public docs 对 benchmark artifact 的联想。

**具体修改**
- 删除 `docs/tutorials/visual-benchmark.md` 的主站入口
- `docs/examples.md` 不再突出 `visual_leaderboard_walkthrough.py`
- 若保留该脚本，移至 `internal/benchmark_artifact/` 或 separate repo

**重点文件**
- `docs/tutorials/visual-benchmark.md`
- `docs/examples.md`
- `mkdocs.yml`
- `examples/visual_leaderboard_walkthrough.py`

**完成标准**
- public docs 不再以 leaderboard heatmap 为 showcase

---

### T07. 下线公开 Agent Tools 页面
**目标**  
避免 reviewer 认为仓库目标混乱。

**具体修改**
- 将 `docs/agent-friendly.md` 从 public docs 导航移除
- 如需保留 agent handoff 文档，放在 repo root/internal docs，不纳入主站

**重点文件**
- `docs/agent-friendly.md`
- `mkdocs.yml`

**完成标准**
- GitHub Pages 主导航无 `Agent Tools`

---

### T08. 新增 machine-learning relevance 页面
**目标**  
增强 De-Time 与 JMLR MLOSS 的契合度。

**具体修改**
- 新增 `docs/ml-workflows.md`
- 内容至少包含：
  - decomposition as preprocessing / denoising / feature extraction
  - integration into downstream ML pipelines
  - one small scikit-learn-facing example
- README 增加链接

**重点文件**
- 新增 `docs/ml-workflows.md`
- `README.md`
- `mkdocs.yml`

**完成标准**
- public docs 中存在清楚的 ML-facing explanation
- reviewer 可以一眼看到“为什么这和 machine learning 社区相关”

---

### T09. 新增 “Why not just use X?” 比较页面
**目标**  
把 related software differentiation 公开化，而不是只写在 paper 里。

**具体修改**
- 新增 `docs/compare.md`
- 小节建议：
  - Why not just use `statsmodels`?
  - Why not just use `PyEMD`?
  - Why not just use `PyWavelets`?
  - Why not just use `PySDKit`?
  - When to prefer `SSALib` over De-Time

**重点文件**
- 新增 `docs/compare.md`
- `mkdocs.yml`

**完成标准**
- 对每个核心 competitor 都有一段诚实的边界说明
- 不再回避 `PySDKit` 和 `SSALib`

---

## Wave 3 — 清理 installable package / sdist / repo boundary

### T10. 把 `synthetic_ts_bench` 从 installable artifact 中移除
**目标**  
切断 sdist 对 benchmark artifact 的直接泄漏。

**具体修改**
- 从 `tool.scikit-build.sdist.include` 中删除 `src/synthetic_ts_bench/**/*.py`
- 如有必要，将 `src/synthetic_ts_bench/` 移到：
  - `contrib/benchmark_artifact/`
  - 或 separate repository

**重点文件**
- `pyproject.toml`
- 目录结构

**完成标准**
- 构建后的 sdist 中不含 `synthetic_ts_bench`

---

### T11. 从 sdist 中移除 reviewer / agent 材料
**目标**  
让 source package 更干净。

**具体修改**
- 从 `pyproject.toml` 和 `MANIFEST.in` 移除：
  - `JMLR_*`
  - `AGENT_MANIFEST*`
  - `AGENT_INPUT_CONTRACT.md`
  - 其他 submission-only 文件
- 仅保留最终用户/开发者需要的内容

**重点文件**
- `pyproject.toml`
- `MANIFEST.in`

**完成标准**
- sdist 解压后不再看到 JMLR / AGENT 材料

---

### T12. 审核 examples/docs 是否应进入 sdist
**目标**  
只保留对 reviewer/user 真有价值的内容。

**具体修改**
- 决定 docs/examples 是否都进入 sdist
- 若保留 examples，删除 benchmark-heavy examples
- 若保留 docs，确保没有 internal-only pages

**重点文件**
- `pyproject.toml`
- `MANIFEST.in`
- `docs/`
- `examples/`

**完成标准**
- sdist 内容能自洽解释为 “software distribution”，而不是 “research repo dump”

---

## Wave 4 — 把工程质量做成硬证据

### T13. 为 coverage 加 fail-under 门槛
**目标**  
把 “有 coverage” 变成 “coverage 被 CI 强制”。

**具体修改**
- 在 CI 覆盖任务中加入 `--cov-fail-under=95` 或更高
- 若当前达不到，先整理测试再逐步抬阈值
- README 加 coverage badge / exact number

**重点文件**
- `.github/workflows/ci.yml`
- `README.md`

**完成标准**
- CI 会因 coverage 低于阈值而失败
- reviewer 能看到明确数值

---

### T14. 统一 coverage story 与 public surface
**目标**  
消除 “public docs 暴露功能，但 coverage 排除” 的矛盾。

**具体修改**
- 评估 `leaderboard.py`：
  - 若仍是 public surface，则取消 `.coveragerc` 中的 omit，并补测试
  - 若不是 public surface，则把它移出 public docs / API / examples
- 对类似模块做同样处理

**重点文件**
- `.coveragerc`
- `docs/api.md`
- `docs/examples.md`
- `mkdocs.yml`
- tests/

**完成标准**
- 不再存在 public-but-untested 的显著矛盾点

---

### T15. 增强 wheel/install 证据
**目标**  
让 release story 不只是 workflow 文件存在，而是真正可信。

**具体修改**
- 确认 `cibuildwheel.toml` 的 smoke tests 覆盖 `detime` canonical path
- 将 wheel-tested platforms / Python versions 写入 README 和 release notes
- 准备 GitHub release notes 模板

**重点文件**
- `cibuildwheel.toml`
- `README.md`
- `.github/workflows/wheels.yml`
- 新增 `.github/release-template.md`（可选）

**完成标准**
- reviewer 不会再问 “你到底有没有验证 wheel 安装路径”

---

## Wave 5 — 补齐同类软件比较和证据

### T16. 重写 `docs/research-positioning.md`
**目标**  
把相关工作比较升级为 reviewer 可接受的版本。

**具体修改**
- 加入 `SSALib`
- 把 `vmdpy` 写法更新为 `sktime`/vmd lineage
- 加强 `PySDKit` 一节，明确 independent delta
- 每个工具写：
  - 其最强之处
  - De-Time 的补位点
  - De-Time 明确不主张超越之处

**重点文件**
- `docs/research-positioning.md`

**完成标准**
- `PySDKit` 和 `SSALib` 成为核心对比对象
- related software 不再显得过时或“挑软柿子捏”

---

### T17. 生成一张公平的软件对比表
**目标**  
让 paper 和 docs 都能复用同一张核心比较表。

**具体修改**
- 新建 `docs/assets/tables/software_comparison.csv` 或 markdown table source
- 维度建议：
  - canonical decomposition result contract
  - batch CLI
  - profiling
  - multivariate support
  - native kernels
  - wrapper transparency
  - release evidence
  - docs/tutorials/API
  - family depth
- 覆盖：
  - De-Time
  - statsmodels
  - PyEMD
  - PyWavelets
  - PySDKit
  - SSALib

**重点文件**
- 新增 `docs/assets/tables/software_comparison.*`
- `docs/compare.md`
- `docs/research-positioning.md`
- `submission/jmlr_mloss_software_paper_draft.md`

**完成标准**
- 一张表就能讲清“De-Time 的软件增量到底是什么”

---

### T18. 生成一组最小可辩护 comparison evidence
**目标**  
给 paper 加一点硬证据，而不是只有定位表述。

**具体修改**
- 新建 `examples/comparison_minimal.py` 或 `benchmarks/minimal_software_comparison.py`
- 至少生成：
  - stable method runtime snapshot（只对 apples-to-apples 的方法）
  - feature matrix
  - output contract comparison
- 注意不要做夸大的 benchmark claims

**重点文件**
- 新增 comparison script
- docs 中加入结果摘要
- paper 中引用结果

**完成标准**
- 至少有一组 reviewer 能引用的事实型 comparison evidence

---

## Wave 6 — submission text / cover letter / final polish

### T19. 重写 software paper 的标题、摘要和 related work
**目标**  
让稿件与实际软件边界一致。

**具体修改**
- 标题避免暗示“all-in-one deeper implementation”
- 摘要明确：
  - not a new algorithm
  - workflow-oriented decomposition software
  - multivariate under one API
  - selected native kernels
  - extracted from earlier artifact
- related work 必须正面对上 `PySDKit`、`SSALib`、`sktime`/VMD story

**重点文件**
- `submission/jmlr_mloss_software_paper_draft.md`

**完成标准**
- reviewer 读完摘要，不会误以为你在 claim 全家族方法深度优势

---

### T20. 在 cover letter 中把 adoption 写得诚实但不自毁
**目标**  
在 adoption 弱的情况下，仍把材料组织到最稳。

**具体修改**
- 保留 “public adoption still early” 的诚实表述
- 但补上：
  - public repo
  - issue tracker
  - docs site
  - release/tag
  - quality gates
  - maintained package identity
- 如果 release 已做，加入 reviewed version frozen evidence

**重点文件**
- `submission/cover_letter_jmlr_mloss.md`

**完成标准**
- reviewer 看到 adoption 弱，但也看到 package 已经进入可审的稳定态

---

### T21. 增加 machine-learning relevance paragraph
**目标**  
强化 venue fit。

**具体修改**
- 在 abstract/introduction/docs 中增加：
  - decomposition for denoising / feature extraction / representation / preprocessing
  - how common software surface reduces friction in ML experiments
- 增加一个 ML-facing example tutorial

**重点文件**
- `submission/jmlr_mloss_software_paper_draft.md`
- `README.md`
- `docs/ml-workflows.md`

**完成标准**
- reviewer 不会轻易说 “this is useful software, but why JMLR?”

---

### T22. 冻结 reviewed version
**目标**  
让 submission 对应一个真实可复现的 reviewed artifact。

**具体修改**
- 创建 GitHub tag / release（例如 `de-time-v0.1.0` 或更高）
- 确保 docs / package / cited URLs 都对应冻结版本
- 如可能，补 Zenodo DOI 或 release archive 引用

**重点文件**
- GitHub release/tag
- `CITATION.cff`
- `README.md`
- paper / cover letter

**完成标准**
- reviewer 能明确知道 “reviewed version” 到底是哪一版

---

## 最终执行顺序（不要乱）

1. **T01–T03**：先做 canonical identity  
2. **T04–T09**：再清 public docs  
3. **T10–T12**：然后清 installable package  
4. **T13–T15**：补工程硬证据  
5. **T16–T18**：补 comparison evidence  
6. **T19–T22**：最后再重写 paper/cover letter 并冻结 release

---

## 一条最重要的执行纪律

**不要先改 paper，再改代码/包边界。**  
因为你当前最危险的问题不在“论文怎么描述”，而在 reviewer 打开 repo 之后会立刻看到的事实：
- `detime` 还是 shim
- docs 还在讲 benchmark / agent
- sdist 还带 benchmark/reviewer 材料

如果这些事实不先改，paper 写得再漂亮也会被代码本身打脸。