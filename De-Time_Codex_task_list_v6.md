# De-Time Codex 可执行任务清单（v6）

说明：以下任务默认按优先级执行。  
状态字段建议：`todo` / `doing` / `done` / `blocked`

---

## Wave 0 — 事实与发布对齐（必须最先做）

### PKG-001 对齐公开安装路径
- **目标**：消除 README / docs / release / PyPI 之间的安装矛盾
- **操作**：
  - 检查 `README.md`
  - 检查 `docs/install.md`
  - 检查 `docs/quickstart.md`
  - 检查 GitHub release 文案
  - 检查 `PUBLISHING.md`
- **执行**：
  - 若 PyPI 已发布：所有文档统一写 `pip install de-time`
  - 若 PyPI 未发布：全部改为 source install / release asset install，并删除已发布表述
- **验收标准**：
  - 全 repo 不再存在与真实发布状态冲突的安装说明
  - grep 检查无旧表述残留

### PKG-002 发布后安装 smoke test
- **目标**：确保安装路径对 reviewer 真实可复现
- **操作文件**：
  - `.github/workflows/wheels.yml`
  - 新增或修改 release verification job
- **执行**：
  - 添加 job：从公开安装渠道安装 `de-time`
  - 运行：
    - `python -c "import detime; print(detime.__version__)"`
    - `detime schema`
    - 最小 quickstart example
- **验收标准**：
  - release CI 绿色
  - 安装来源明确记录在日志

### PKG-003 统一 package identity 文案
- **目标**：统一 distribution / import / legacy alias
- **操作文件**：
  - `README.md`
  - `docs/migration.md`
  - `docs/architecture.md`
  - `PUBLISHING.md`
  - `src/tsdecomp/__init__.py`
- **执行**：
  - 统一写法：
    - distribution: `de-time`
    - canonical import: `detime`
    - legacy alias: `tsdecomp`
    - deprecation horizon: 明确写多少个 release cycle
- **验收标准**：
  - 全站文案一致
  - `tsdecomp` 不再被描述为主实现

---

## Wave 1 — JMLR 核心阻断项

### TEST-001 输出双层 coverage
- **目标**：把 coverage 从单一数字改成 reviewer 可理解的两层结构
- **操作文件**：
  - `docs/reproducibility.md`
  - `.coveragerc`
  - `.github/workflows/ci.yml`
- **执行**：
  - 输出两类 coverage：
    1. core-surface coverage
    2. package-wide coverage
  - 在 docs 写明 omit 列表和理由
- **验收标准**：
  - reviewer 可以一眼看懂 coverage 分母
  - CI artifact 包含 coverage 明细

### TEST-002 扩展 package-wide smoke tests
- **目标**：降低“只测核心、不测全包”的攻击点
- **操作文件**：
  - `tests/`
  - `.github/workflows/ci.yml`
- **执行**：
  - 为以下模块至少加 smoke tests：
    - CLI
    - I/O
    - serialization
    - representative wrapper methods
    - visualization stubs / exports（若 public）
- **验收标准**：
  - package-wide smoke 通过
  - package-wide coverage 明显高于当前 baseline

### TEST-003 native vs fallback 一致性测试
- **目标**：证明 native speedup 不以 correctness 为代价
- **操作文件**：
  - `tests/test_native_agreement_*.py`
  - `src/detime/_native.py` 相关调用点
- **执行**：
  - 对 SSA / STD / STDR 增加 numeric agreement tests
  - 比较：
    - trend / season / residual
    - summary metrics
    - tolerance documented
- **验收标准**：
  - native / python fallback 结果在容忍误差内一致

### TEST-004 method catalog regression tests
- **目标**：稳定 machine-facing catalog contract
- **操作文件**：
  - `tests/test_registry_catalog.py`
  - `src/detime/registry.py`
- **执行**：
  - 固定 key schema
  - 测试 flagship / wrapper / optional labels
  - 测试 capability fields 完整性
- **验收标准**：
  - `list_catalog()` 输出结构稳定
  - 缺字段会 CI fail

### REL-001 adoption 证据采集
- **目标**：让 cover letter 不再只有“early adoption”
- **操作文件**：
  - `submission/cover_letter*.md`
  - 新增 `submission/adoption_evidence.md`
- **执行**：
  - 汇总外部 issue、discussion、fork、notebook、lab usage、downloads、teaching use
  - 如果外部证据仍少，补 grounded internal multi-project reuse evidence
- **验收标准**：
  - cover letter 至少有 2–4 条具体 adoption proxies
  - 不使用空泛措辞

---

## Wave 2 — related software 与比较实验

### CMP-001 新建 reviewer-grade comparison matrix
- **目标**：从定性比较升级为编辑可用的选型矩阵
- **操作文件**：
  - `docs/comparisons.md`
  - 新增 `docs/comparison-evidence.md`
- **执行**：
  - 加入对象：
    - statsmodels
    - PyEMD
    - PyWavelets
    - PySDKit
    - SSALib
    - sktime
  - 维度：
    - common config object
    - common result object
    - machine-readable catalog
    - batch CLI
    - profiling
    - multivariate
    - native-backed
    - maturity labeling
    - compact output
    - MCP/tool surface
- **验收标准**：
  - comparisons 页面不再只讲 scope
  - 至少一张表可直接搬进 paper

### CMP-002 nearest competitor 深度对位：PySDKit
- **目标**：单独回答“为什么不是 PySDKit”
- **操作文件**：
  - `docs/comparisons.md`
  - `submission/software_paper_draft*.md` 或等价 paper 文件
- **执行**：
  - 单独写一小节：
    - PySDKit 强项
    - De-Time 非重合强项
    - 公平边界
- **验收标准**：
  - 能明确说出不是“我们也统一接口”，而是“workflow/machine-facing/result contract 的差异”

### CMP-003 SSA 对位：SSALib
- **目标**：回答“为什么不是 SSALib”
- **操作文件**：
  - `docs/comparisons.md`
  - paper related software
- **执行**：
  - 对比：
    - SSA family depth
    - Monte Carlo SSA / viz / solver depth
    - unified toolkit vs specialist SSA depth
- **验收标准**：
  - paper 中不再回避 SSA specialist competitor

### BENCH-001 runtime comparison scripts
- **目标**：提供 reviewer 可复验的 runtime evidence
- **操作文件**：
  - 新增 `benchmarks/software_comparison/`
  - docs / reproducibility 页面
- **执行**：
  - 只对公平任务做 benchmark：
    - STL / MSTL path
    - SSA path
    - EMD path
    - wavelet path
    - native flagship methods
  - 输出 CSV + Markdown summary
- **验收标准**：
  - benchmark 脚本一键运行
  - paper 可以引用结果表

### BENCH-002 workflow-level comparison demo
- **目标**：证明 De-Time 的价值在 workflow abstraction
- **操作文件**：
  - 新增 `examples/workflow_comparisons/`
  - `docs/why.md`
  - `docs/ml-workflows.md`
- **执行**：
  - 用同一个研究工作流分别展示：
    - 手工 glue 多个 specialist packages
    - 用 De-Time 统一完成
- **验收标准**：
  - reviewer 可直观看到接口碎片化 vs 统一接口差异

---

## Wave 3 — agent-friendly / token-aware 强化

### AGENT-001 建立 token benchmark
- **目标**：把“low-token”变成有数字的 claim
- **操作文件**：
  - 新增 `benchmarks/token_benchmarks/`
  - `docs/token-benchmarks.md`
- **执行**：
  - 测量：
    - full / summary / meta
    - univariate / multivariate
    - short / medium / long sequences
  - 输出近似 token counts
- **验收标准**：
  - 文档里至少有 1 张表 + 1 张图
  - 任何 low-token claim 都有 benchmark 引用

### AGENT-002 machine API 页面
- **目标**：把 machine-facing story 文档化
- **操作文件**：
  - 新增 `docs/machine-api.md` 或 `docs/agent.md`
  - `mkdocs.yml`
- **执行**：
  - 说明：
    - schema assets
    - catalog
    - recommend
    - serialization modes
    - artifact contract
    - MCP server
- **验收标准**：
  - 主导航可见
  - reviewer 可单独阅读 machine-facing surface

### AGENT-003 MCP 公开叙事升级
- **目标**：把 MCP 从“命令入口”升级为“稳定工具接口”
- **操作文件**：
  - `docs/machine-api.md`
  - `AGENT_MANIFEST.json`
  - `ENTRYPOINTS.md`
- **执行**：
  - 明确写：
    - 当前 local-first 还是 remote-ready
    - tool names
    - versioning policy
    - recommended tool subsets
- **验收标准**：
  - MCP story 自洽
  - 不夸大 remote/discovery status

### AGENT-004 agent eval harness
- **目标**：验证 agent 真能用，不只是有工具
- **操作文件**：
  - 新增 `evals/agent/`
  - `docs/machine-api.md`
- **执行**：
  - 设计 5–10 条 deterministic tasks：
    - list methods
    - recommend method
    - get schema
    - run decompose
    - summarize result
    - bounded context task
- **验收标准**：
  - eval 可重复
  - 至少有 pass/fail summary

### AGENT-005 capability cards
- **目标**：让每个方法对人和机器都可解释
- **操作文件**：
  - `src/detime/registry.py`
  - `docs/method-cards.md`
  - method docs pages
- **执行**：
  - 每个方法补：
    - assumptions
    - failure modes
    - maturity
    - native-backed?
    - optional deps?
    - multivariate?
    - recommended tasks
- **验收标准**：
  - docs 与 catalog 对齐
  - method card 信息完整

---

## Wave 4 — paper / cover letter / reviewer package

### PAPER-001 重写 abstract 和 introduction
- **目标**：把主线压回 software abstraction
- **操作文件**：
  - software paper draft
- **执行**：
  - 明确：
    - not a new decomposition algorithm
    - workflow-oriented software layer
    - machine-facing interface
    - specialist-libraries complement, not replacement
- **验收标准**：
  - 摘要和引言第一段不再像 benchmark / methods paper

### PAPER-002 重写 related software
- **目标**：让 reviewer 不会说你回避最危险对手
- **操作文件**：
  - software paper related work
- **执行**：
  - 结构：
    - specialists
    - nearest unified competitor
    - ecosystem continuation projects
  - 强调 PySDKit / SSALib
- **验收标准**：
  - 至少两段专门讨论 PySDKit 和 SSALib

### PAPER-003 增加 software evidence tables
- **目标**：把 docs comparison 直接转成 paper-grade 表格
- **操作文件**：
  - paper tables
- **执行**：
  - 加入：
    - capability matrix
    - install/release matrix
    - runtime snapshot
    - machine-facing matrix
- **验收标准**：
  - paper 中至少 3 张硬表

### PAPER-004 companion relationship section
- **目标**：防止被说成 benchmark artifact repackaging
- **操作文件**：
  - paper
  - cover letter
- **执行**：
  - 明确：
    - benchmark repo 关系
    - Dec-SR / companion paper 关系
    - De-Time 独立软件边界
- **验收标准**：
  - reviewer 读完不会再问“到底哪个才是主贡献对象”

### PAPER-005 cover letter 事实核对
- **目标**：不让 cover letter 成为硬伤来源
- **操作文件**：
  - `submission/cover_letter*.md`
- **执行**：
  - 检查：
    - version
    - release path
    - install
    - website
    - adoption evidence
    - CI
    - docs
- **验收标准**：
  - cover letter 中没有任何 public fact 可被 reviewer 一步反驳

### SUB-001 reviewer bundle
- **目标**：降低 reviewer 搜索成本
- **操作文件**：
  - 新增 `submission/reviewer_bundle/`
- **执行**：
  - 包含：
    - `REVIEWER_SOFTWARE_MATRIX.md`
    - `INSTALL_VERIFICATION.md`
    - `TESTING_AND_COVERAGE.md`
    - `COMPANION_RELATIONSHIP.md`
    - `AGENT_INTERFACE_OVERVIEW.md`
- **验收标准**：
  - reviewer bundle 可单独阅读
  - 所有关键问题都能在 bundle 中找到直接答案

---

## 建议执行顺序（最短路径）

1. PKG-001  
2. PKG-002  
3. PKG-003  
4. TEST-001  
5. TEST-002  
6. REL-001  
7. CMP-001 / CMP-002 / CMP-003  
8. BENCH-001 / BENCH-002  
9. AGENT-001 / AGENT-002 / AGENT-004  
10. PAPER-001 / PAPER-002 / PAPER-003 / PAPER-004 / PAPER-005  
11. SUB-001

---

## 最终交付定义

当以下条件同时满足时，才进入“可投 JMLR”状态：

- 安装说明与真实发布状态完全一致
- related software 比较包含 PySDKit / SSALib 且有硬证据
- coverage 口径诚实清晰，测试证据扩大
- adoption evidence 不再只有“still early”
- machine-facing / agent-friendly claim 有 benchmark 或 eval 支撑
- software paper 主线明确是 workflow/machine-facing software layer
