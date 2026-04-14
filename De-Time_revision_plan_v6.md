# De-Time 修改开发计划（网页 + 软件包 + JMLR + agent 方向）

版本：v6  
目标：把 De-Time 从“接近可投”推进到“JMLR MLOSS 可正式提交”的状态，同时把 agent-friendly 叙事从附加项升级为明确优势。

---

## 一、总目标

本轮开发不是“继续加方法”，而是完成四件事：

1. **事实对齐**：公开网站、README、release、package metadata、PyPI 状态完全一致。
2. **审稿对齐**：按 JMLR MLOSS 的 review criteria 补齐最会被攻击的证据。
3. **竞争对齐**：把与 PySDKit / SSALib / statsmodels / PyEMD / PyWavelets / sktime 的比较做成 reviewer-grade。
4. **未来对齐**：把 De-Time 从“有 agent features”推进到“可被认为是 2026 式 machine-facing scientific software”。

---

## 二、现状诊断

## 2.1 已完成的关键进步
- `detime` 已基本转为 canonical package surface。
- `tsdecomp` 已缩为窄兼容层。
- docs 主导航已明显去 benchmark artifact 化。
- CI / docs / wheels / release tag / GitHub release 已经成链。
- machine-facing surface 已经真实存在：schema / catalog / recommend / summary/meta / MCP / AGENT manifest。
- companion benchmark repo 已分离。

## 2.2 当前主要阻断项
1. **PyPI/public install 不一致**
2. **active user community 证据弱**
3. **related software 实证比较不足**
4. **coverage 口径仍有 reviewer attack surface**
5. **agent-native 叙事尚未形成公开可验证证据**
6. **paper 与 software story 仍可能被 benchmark / Dec-SR 拖偏**

---

## 三、工作流总览（建议顺序）

### Wave 0：事实与发布对齐（必须先做）
### Wave 1：JMLR 核心阻断项清除
### Wave 2：related software 与比较实验补强
### Wave 3：agent-friendly / token-aware 证据化
### Wave 4：paper / cover letter / reviewer package 收口

---

## 四、Wave 0：事实与发布对齐

## 4.1 目标
任何 reviewer 打开 README、docs、GitHub release、PyPI、安装命令，看到的都是**同一个事实**。

## 4.2 需要解决的问题
目前最危险的问题是：  
你在 README / docs 中把 `pip install de-time` 写成公开可用路径，但如果 PyPI 还没上线，reviewer 会立刻判定 public software path 不可信。

## 4.3 修改内容

### A. 如果你准备立刻发布 PyPI
- 真的发布 `de-time==0.1.0`（或 0.1.1）
- 确认 package metadata、README badges、docs install 页面、release note 全部同步
- 发布后加一条自动 smoke test：从 PyPI 拉下 wheel / sdist 安装并跑 `detime schema`

### B. 如果你暂时不发布 PyPI
- 删除所有“已可 `pip install de-time`”的陈述
- 改成：
  - 推荐 `pip install git+https://...`
  - 或 “PyPI release pending; use GitHub source install”
- README、docs/install.md、quickstart、release notes、paper draft、cover letter 全部同步

## 4.4 涉及文件
- `README.md`
- `docs/install.md`
- `docs/quickstart.md`
- `docs/index.md`
- `pyproject.toml`
- `.github/workflows/wheels.yml`
- `PUBLISHING.md`
- `CHANGELOG.md`（若有）
- submission 文档中的 release 描述

## 4.5 完成标准
- 任意 public-facing 页面不再出现互相矛盾的安装叙述
- reviewer 可以按文档真实完成安装
- 若 PyPI 上线，则 CI 自动验证来自 PyPI 的安装路径

---

## 五、Wave 1：JMLR 核心阻断项清除

## 5.1 目标
把最容易导致 weak reject / major concern 的点降到可辩护区间。

## 5.2 任务 1：把 package identity 写得无懈可击

### 需要做什么
- 在 docs/migration、architecture、PUBLISHING、paper 中统一写明：
  - canonical package = `detime`
  - distribution name = `de-time`
  - `tsdecomp` = deprecated compatibility alias
  - 兼容期多久
  - 之后如何 retire

### 为什么
 reviewer 最怕“一个软件两个名字三个身份”。

### 完成标准
- 所有地方对名字、导入路径、兼容策略的描述完全一致
- 没有任何页面仍暗示 `tsdecomp` 是主实现

## 5.3 任务 2：把 coverage 叙事改成“诚实 + 更硬”

### 需要做什么
- 公布两套 coverage：
  1. **core-surface coverage**
  2. **package-wide coverage**
- 在 docs/reproducibility 中明确哪些模块被 omit、为什么 omit
- 争取把 package-wide coverage 拉高；若拉不高，至少把 smoke test 和 contract test 补上
- 增加 numerical agreement tests（native vs python fallback）

### 为什么
JMLR reviewer 会质疑“93.2% 是不是只测了你最想测的部分”。

### 完成标准
- reviewer 一眼能看懂 coverage 分母
- CI 里有可复现 coverage artifact
- native-backed paths 有 explicit agreement test

## 5.4 任务 3：补 adoption / user community 证据

### 需要做什么
- 收集至少下列证据之一：
  - 外部 issue / bug report / discussion
  - 外部 notebook / 教学材料 / lab usage
  - package downloads（如果 PyPI 发布）
  - benchmark repo / software repo 被外部 fork/use 的证据
  - 研究组内多个项目复用的 grounded summary
- 在 cover letter 中诚实写：
  - 仍然是 early-stage public adoption
  - 但已经有何种 concrete reuse evidence

### 为什么
JMLR 把 active user community 写得很明确；即便达不到强社区，也要有更像样的 proxy。

### 完成标准
- cover letter 不再只写“still early”
- 至少有 2–4 个具体 adoption proxies

---

## 六、Wave 2：related software 与比较实验补强

## 6.1 总原则
不要追求“比所有人都强”，而要证明：

> De-Time 在“统一工作流 + 机器接口 + 研究软件边界”这个维度上，确实填补了生态空白。

## 6.2 必须正面对比的对象

### 第一优先级
- PySDKit
- SSALib

### 第二优先级
- statsmodels
- PyEMD
- PyWavelets
- sktime（尤其 VMD continuation）

## 6.3 必补的五张表

### 表 A：Reviewer-grade software capability matrix
列建议：
- package
- primary scope
- unified config object
- unified result object
- machine-readable method catalog
- CLI batch path
- profiling path
- multivariate support
- maturity labeling
- machine-facing compact output
- MCP / tool surface

### 表 B：Install / release / reproducibility matrix
列建议：
- public release
- PyPI
- GitHub release
- wheels
- CI platforms
- docs website
- tutorial
- API docs
- coverage disclosure
- reproducibility script

### 表 C：Method-family fairness table
按 family 公平比：
- classical decomposition: vs statsmodels
- SSA: vs SSALib
- EMD/CEEMDAN: vs PyEMD
- wavelet workflows: vs PyWavelets
- unified toolkit layer: vs PySDKit

### 表 D：Runtime / memory / scaling table
只比公平、可复现的任务：
- SSA native vs SSALib / pure Python fallback
- STD / STDR native vs own fallback
- maybe batch orchestration overhead vs plain hand-written glue

### 表 E：Agent-friendly matrix
列建议：
- JSON schema assets
- compact serialization levels
- recommend interface
- machine-readable catalog
- MCP endpoint
- artifact contract
- token benchmark
- tool evals

## 6.4 必须补的实验

### 实验 1：公平的 runtime comparison
- 只对“你真正主打的 methods”做
- 不要对 wrapper methods 乱比
- 加：
  - exact environment
  - input sizes
  - repeated runs
  - mean/std
  - correctness agreement

### 实验 2：workflow-level comparison
让 reviewer 看到：
- 用 statsmodels / PyEMD / PyWavelets / SSALib / PySDKit 分别完成同一个研究 workflow 有多碎片化
- 用 De-Time 一次完成同一个 workflow 的差异

这个实验不需要夸张 benchmark，只要真实。

### 实验 3：machine-facing comparison
比较：
- full vs summary vs meta 的 payload size
- CLI vs schema vs MCP 路径
- recommended method path 与 manual path 的差异

---

## 七、Wave 3：agent-friendly / token-aware 证据化

## 7.1 目标
把“我们适合 agent”从一句愿景，变成 reviewer 可验证的软件性质。

## 7.2 任务 1：补 token benchmark

### 要做什么
对典型任务输出测量：
- `full` JSON token size
- `summary` JSON token size
- `meta` JSON token size
- 单变量 vs 多变量
- 短序列 vs 长序列

### 建议输出
- 表格 + 图
- docs/agent.md 或 docs/machine-api.md 页面
- 一个 CI/bench script 可复现

### 完成标准
- 任何“low-token” claim 都有数字支持

## 7.3 任务 2：补 agent eval harness

### 要做什么
建立最小 agent regression tests：
- 给定 series metadata，agent 能否调用 `recommend`
- 能否正确读取 schema
- 能否先用 `summary` 再决定是否取 full
- 能否在限定上下文预算下完成 decomposition and report

### 完成标准
- 至少有 5–10 条 deterministic evals
- 文档里能公开解释 pass/fail

## 7.4 任务 3：把 MCP 叙事升级

### 要做什么
- 增加 docs/mcp.md 或 docs/agents.md
- 说明：
  - 当前支持 local MCP
  - 推荐 tool subsets
  - stable method catalog endpoint
  - schema versioning strategy
- 如果有能力，额外给出 remote MCP deployment example
- 如果没有 remote，也要诚实写“currently local-first”

### 完成标准
- MCP 不再只是入口命令，而是完整机器接口 story

## 7.5 任务 4：加 capability cards / method cards

### 每个方法卡至少包含
- family
- primary assumptions
- failure modes
- maturity
- native-backed?
- optional dependencies?
- multivariate?
- recommended tasks
- not recommended for

### 完成标准
- 方法页和 machine-facing catalog 都能表达这些信息

---

## 八、Wave 4：paper / cover letter / reviewer package 收口

## 8.1 software paper 应该怎么写

### 核心主线
> De-Time is a reusable workflow-oriented and machine-facing software layer for time-series decomposition across fragmented specialist ecosystems.

### 不该作为主线的内容
- benchmark scientific findings
- Dec-SR 的 scientific claims
- “我们支持很多方法”
- “我们也能做 symbolic regression”

这些内容都应该降为：
- downstream utility evidence
- companion ecosystem evidence

## 8.2 论文结构建议

### 1. Introduction
- 讲 fragmented decomposition ecosystem
- 讲缺少统一 workflow / result contract / machine interface
- 明确不是新算法

### 2. Scope and contribution
- unified config/result contract
- deterministic CLI + batch workflow
- selective native acceleration
- machine-facing schemas / compact outputs / recommendation / MCP

### 3. Related software
- specialists vs unified competitor
- 把 PySDKit / SSALib 放中心
- 用 reviewer-grade table

### 4. Architecture
- `detime` core
- legacy `tsdecomp` compatibility boundary
- flagship vs wrapper vs optional backend

### 5. Quality / reproducibility
- CI matrix
- wheels
- coverage (honest)
- performance snapshots
- docs / tutorials / migration
- dist-content checks

### 6. Relationship to benchmark / Dec-SR ecosystem
- companion repos / companion papers
- software contribution remains independent

### 7. Limitations
- no algorithmic novelty
- external adoption still early
- not all methods equally mature
- agent-native story still evolving

## 8.3 cover letter 应该怎么改

### 必写
- current released version
- exact install path
- website
- CI / docs / wheels evidence
- active user community evidence（哪怕仍早期，也要具体）
- relation to companion benchmark and Dec-SR papers
- why this is independent software, not artifact extraction

### 不要写
- “will release upon acceptance” 如果实际上很多内容已经公开
- “PyPI available” 如果还没公开
- “extensive community” 如果证据不够

## 8.4 reviewer package 应该准备什么
建议新增 `submission/reviewer_bundle/` 或等价目录：

- `REVIEWER_SOFTWARE_MATRIX.md`
- `RELEASE_STATE.md`
- `INSTALL_VERIFICATION.md`
- `TESTING_AND_COVERAGE.md`
- `COMPANION_RELATIONSHIP.md`
- `AGENT_INTERFACE_OVERVIEW.md`

---

## 九、网页修改建议（docs / website）

## 9.1 首页应该强调什么
首页只保留四个信息：

1. what De-Time is
2. what it is not
3. why it is useful
4. how to install and start

### 首页一句话建议
> De-Time is a workflow-oriented, machine-facing decomposition library that standardizes results, configuration, and downstream integration across fragmented time-series decomposition methods.

## 9.2 首页不该出现什么
- benchmark leaderboard 风格叙事
- 夸张 scientific claims
- 模糊的 install state
- 暗示所有方法等成熟

## 9.3 新增页面建议
- `docs/agent.md` 或 `docs/machine-api.md`
- `docs/method-cards.md`
- `docs/release-state.md`
- `docs/comparison-evidence.md`
- `docs/token-benchmarks.md`

## 9.4 comparisons 页面需要升级
从“定位比较”升级为“选型比较”：
- 哪种用户应该选哪种包
- De-Time 的空白填补在哪里
- 何时不要选 De-Time，而应直接选 specialist package

这种诚实会显著提升可信度。

---

## 十、软件包修改建议（package / code / release）

## 10.1 package 层
- 确保 `detime` 是唯一 canonical surface
- `tsdecomp` deprecation warning 更明确
- `list_catalog()` 输出补全 capability metadata
- `summary/meta` 输出模式写入 schema 文件
- 增加 `token_profile` helper（可选）

## 10.2 release 层
- 发布真实 PyPI 或移除 PyPI claim
- 发布 wheels 后自动 smoke install
- 在 GitHub release 附：
  - wheels / sdist
  - release verification notes
  - compatibility notes
  - benchmark companion note

## 10.3 testing 层
- 增加 package-wide smoke matrix
- 增加 schema stability tests
- 增加 summary/meta token regression tests
- 增加 native vs fallback numerical agreement tests
- 增加 method-catalog regression tests

---

## 十一、完成后的预期状态

如果按上面顺序做完，你的软件状态会从：

> “有潜力，但 reviewer 仍有多个硬攻击点”

变成：

> “定位清楚、发布可信、比较充分、机器接口有新意、即便社区仍早期也足以进入 JMLR 讨论区间”

---

## 十二、最终执行顺序（最短路径）

### 第一步
修 PyPI / install / release truthfulness

### 第二步
补 reviewer-grade comparison（尤其 PySDKit / SSALib）

### 第三步
修 coverage 叙事 + 增加 package-wide evidence

### 第四步
补 adoption proxies

### 第五步
补 token benchmark + agent eval

### 第六步
重写 paper / cover letter

---

## 十三、一句话总结

**De-Time 现在最需要的不是更多方法，而是更少矛盾、更硬比较、更诚实质量证据，以及把 machine-facing 优势正式写成可验证的软件贡献。**
