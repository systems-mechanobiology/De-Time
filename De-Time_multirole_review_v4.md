# De-Time 多角色重审（2026-04-08）

## 一页结论

这次修改**明显比上一轮成熟很多**。最重要的改进有四个：

1. **软件身份基本清楚了**：`detime` 已经成为规范入口；`tsdecomp` 被收缩成兼容层。
2. **打包边界大幅收紧**：`CMakeLists.txt`、`pyproject.toml`、`MANIFEST.in`、`scripts/check_dist_contents.py` 基本朝同一方向收敛。
3. **主文档站去 benchmark 化**：主导航不再把 benchmark/leaderboard 当作主入口。
4. **related software 终于开始正面对手**：`PySDKit`、`SSALib`、`sktime` 已进入公开比较页面。

但如果我分别戴上四顶帽子来审：

- **机器学习专家**：有价值，但不是“定义赛道”的软件；更像一个很聪明的 workflow layer。
- **时间序列工程师**：架构已经像一个能维护的软件包了，但 release、证据链和 method maturity 还没完全压实。
- **Nature Machine Intelligence 审稿人**：**拒稿**。软件本身还不足以支撑 NMI 所需的“概念推进 + 科学影响”。
- **JMLR MLOSS 审稿人**：从“明显 weak reject”上升到了“**borderline weak reject / major revision**”。现在最大的阻断点已经不是 package chaos，而是 **公开 release/adoption 证据、对同类软件的系统比较、以及 reviewer-facing 文件的一致性**。

一句话判断：

> **De-Time 现在已经像“可投稿的软件雏形”，但还不是“让 JMLR software track 审稿人放心放行”的成品。**  
> **它已经是“agent-legible”，但还不是 2026 语境下真正“agent-native”的时间序列分解软件。**

---

## 0. 这轮修改后，我认为真正变好的地方

### 0.1 软件身份修正是实质性进步

目前仓库公开叙事已经明确：

- 产品名是 **De-Time**
- distribution 是 **`de-time`**
- canonical import 是 **`detime`**
- `tsdecomp` 只保留顶层 import/CLI 兼容层

这比之前“新旧身份并存、边界混乱”的状态好很多。  
如果 reviewer 只看 README、PUBLISHING 和 install docs，会比上一轮更容易理解你在卖什么。

### 0.2 构建/打包边界大体收敛

这轮最关键的工程修正，不是文案，而是构建规则：

- `CMakeLists.txt` 现在只安装 `src/detime/` 和极窄的 `src/tsdecomp/` 兼容入口。
- `scripts/check_dist_contents.py` 明确限制 `tsdecomp` wheel/sdist 中允许出现的兼容文件。
- `pyproject.toml` 的 sdist include 已经收缩为 `src/detime/**/*.py` 与四个 `src/tsdecomp` 兼容文件，而不是整个旧树。
- `MANIFEST.in` 也在排除 `submission/**`、`AGENT_*`、`JMLR_*`、benchmark tutorial 页面。

这说明你不是只在 README 里说“我已经独立了”，而是真开始把 distribution boundary 做干净了。

### 0.3 公共网页的主叙事更对了

当前 `mkdocs.yml` 的主导航已经围绕：

- Why De-Time
- Install / Quickstart
- Choose a Method
- ML Workflows
- Methods / API / Architecture
- Comparisons / Migration / Reproducibility

展开，而不是把 benchmark heatmap / leaderboard / agent docs 挂在主导航最显眼位置。  
这对 JMLR software reviewer 很重要，因为 reviewer 会默认“导航即软件自我定位”。

### 0.4 related software 的诚实度上升

`docs/comparisons.md` 终于把最危险的对手写进来了：

- `PySDKit`
- `SSALib`
- `sktime`（而不是只盯着旧 `vmdpy` 身份）
- 以及 `statsmodels` / `PyEMD` / `PyWavelets`

这说明你已经从“安全地挑几个好打的对手”转向“正面承认赛道里真实存在的成熟实现”。

---

## 1. 角色一：机器学习专家视角

## 1.1 我会怎么概括你的贡献

从 ML 视角看，De-Time 的真正价值不是“你实现了多少分解算法”，而是：

1. **把异构分解方法拉进一个统一 contract**
2. **让 decomposition 变成一个可组合、可对比、可落盘、可进入下游 ML pipeline 的软件层**
3. **在少数高频路径上给出 native-backed acceleration**
4. **把 univariate / multivariate / CLI / profiling 放在一个比较统一的入口上**

这类贡献是有意义的，尤其当你后面还有 benchmark paper 和 Dec-SR paper 时，它会自然成为整个研究程序的“软件脊柱”。

## 1.2 这个软件的 ML 价值在哪里

### 优点

**(a) 统一 contract 真的有研究价值**

如果你做的是 decomposition benchmark、decompose-then-regress、或结构化时间序列表示学习，那么稳定的 `DecompositionConfig` / `DecompResult` / `decompose()` contract，本身就能显著降低实验系统复杂度。  
这不是花哨包装，而是研究基础设施。

**(b) 你把“方法切换成本”压低了**

对研究者最有价值的不是“多一个方法名”，而是：

- 输入 shape 不用每次重新适配
- 输出字段稳定
- batch/profile/CLI 有统一入口
- metadata 可被后续脚本消费

这一点对 benchmark 和 agent pipeline 都有直接价值。

**(c) 你没有假装算法创新**

这是优点。  
你公开写清楚“De-Time 不是新 decomposition algorithm”，这比很多软件论文把 orchestration layer 伪装成算法创新要诚实得多。

### 缺点

**(a) 贡献层级仍偏“workflow layer”，不是“method-defining software”**

如果 reviewer 很 mean，他会说：

> 你不是做了一个新的 decomposition family，也不是某个 family 的 SOTA implementation；  
> 你做的是一个跨 family 的 orchestration / workflow surface。

这并不是没有价值，但它会直接影响 novelty judgement。

**(b) 你现在最强的 scientific differentiator 还没完全进入主软件叙事**

你两篇稿子实际上已经把更强的科研主线写出来了：

- decomposition as standalone component-recovery task
- decomposition-first symbolic regression
- decomposition as continuous feature decoupling prior

也就是说，软件最有潜力的地方不是“方法菜单”，而是**它能否成为 decomposition → downstream scientific discovery 的统一基础层**。

如果 De-Time 继续只把自己写成“一个统一分解包”，它会低估自己真正可能赢的方向。

## 1.3 作为 ML 专家，我的判断

### 结论

**这是一个有研究基础设施价值的软件，但目前还不是一个足以单独震撼顶级 ML 审稿人的软件对象。**

### 我会给的判断

- **novelty**：中等
- **feasibility**：高
- **evidence base**：中等偏弱
- **scientific extensibility**：高
- **current standalone impact**：中等

### 最关键建议

把软件定位从：

> “many decomposition methods in one package”

改成：

> “a benchmark-backed, workflow-oriented decomposition substrate for component recovery and downstream structure discovery”

也就是把 **De-Time → benchmark → Dec-SR** 串成一条研究程序，而不是让软件停在“统一 API”这层。

---

## 2. 角色二：时间序列工程师视角

## 2.1 工程上我认可的部分

### (1) 公共 API 开始有边界感

这轮最值得肯定的点是：  
你不是把所有内部文件都假装成 public API，而是把公共面尽量压缩到：

- `decompose(series, config)`
- `DecompositionConfig`
- `DecompResult`
- `detime run / batch / profile`

这很对。  
时间序列软件最怕“所有模块都半公开”，因为很快就会把自己绑死。

### (2) CI / docs / wheel / coverage 已经像软件了

你现在至少具备：

- 多平台 CI
- coverage job
- docs strict build
- wheel + sdist smoke test
- content checker
- fail-under=90

这不是顶级成熟度，但已经不是“实验脚本仓库”。

### (3) method positioning 比前一版清楚

你现在已经在公开文档里承认：

- 有旗舰路径
- 有 wrapper
- 有 optional backend
- 不同方法成熟度不同

这比“所有方法都平起平坐”强很多。

## 2.2 作为工程师，我仍然会挑的硬伤

### (1) 还没有真正的 release reality

现在最尴尬的是：

- 没有 GitHub release
- 没有 tags
- 还没有真正 PyPI 发布
- 公开安装仍然依赖 GitHub URL

这意味着你现在是**review snapshot**，不是一个真正完成首发的软件。  
对工程 reviewer 来说，这会影响可部署性、可引用性、可追溯性。

### (2) reviewer-facing 文件仍然自相矛盾

你已经把 package boundary 做得比之前干净很多，但 reviewer 文档没完全跟上：

- `JMLR_MLOSS_CHECKLIST.md` 仍然写成 `tsdecomp`，而且还把 `DR_TS_REG` 视作 core library method。
- `JMLR_SOFTWARE_IMPROVEMENTS.md` 还把 `DR_TS_REG` 写成 native-accelerated retained method。
- `JMLR_SUBMISSION_CHECKLIST.md` 则已经是 De-Time 版本。

这类矛盾会给 reviewer 一个非常糟糕的信号：

> 你到底是已经完成边界重构，还是只是局部改了一半？

### (3) benchmark residue 还没有完全出清

虽然主导航已经清爽很多，但残留内容仍在：

- `docs/examples.md` 仍然列 `visual_leaderboard_walkthrough.py`
- 仍然展示 “Benchmark heatmap walkthrough”
- 还指向 `tutorials/visual-benchmark.md`
- 但这个 benchmark tutorial 又被 `MANIFEST.in` 显式排除了

这会形成一种新的小型不一致：

> 文档内容里还在引导用户走 benchmark 可视化路径，  
> 但发布工件又试图把这些页面从 package 中移除。

### (4) “companion benchmark repo” 还不够落地

README 已经说 benchmark-derived methods moved to `de-time-bench`。  
这句话方向是对的，但如果你不把它变成：

- 一个可点开的公开 companion repo
- 一个清晰的 scope split
- 一个独立文档站 / release path

那 reviewer 会觉得这只是“口头切割”。

### (5) 你还没有 regime-aware intelligence

从时间序列工程角度，下一代 decomposition 软件最需要的不是更多 method names，而是：

- unknown-period support
- drift-aware / chirp-aware support
- regime-shift / change-point awareness
- decomposition quality diagnostics
- method recommender

你 benchmark 稿子自己也已经指出 unknown-period 与 change-point localization 还没正面解决。  
如果 De-Time 想成为真正的“下一代分解软件”，它不能一直停留在“方法统一入口”，而要开始提供“**什么时候该用哪个方法、为什么失败**”的工程能力。

## 2.3 工程结论

**现在的 De-Time 已经是“像样的软件包”，但还不是“成熟发布的软件产品”。**

---

## 3. 角色三：假扮 Nature Machine Intelligence 审稿人

## 3.1 先说结论

**如果你拿 De-Time 软件本身去投 Nature Machine Intelligence，我会拒稿。**

不是因为它没用，而是因为它现在还不满足 NMI 对“研究文章”的期望重心。

## 3.2 为什么我会拒

### (1) 软件本身不构成足够强的概念推进

NMI 更看重：

- 对 ML / AI 的概念性推进
- 或者 AI 对其他科学领域的显著推进
- 或者明确跨学科影响

单独的 De-Time 软件，目前更像：

- 一个工程很认真的 decomposition workflow layer
- 一个研究程序中的中间基础设施
- 而不是一个本身就足够强的 scientific contribution

### (2) 你的强故事不在软件，而在“软件支撑的科学命题”

你上传的两篇稿子里，更像 NMI 稿子的其实是：

- **decomposition as standalone component-recovery task**
- **decomposition-first symbolic regression**
- **continuous feature decoupling as prerequisite for discrete symbolic search**

换句话说，NMI 真正会感兴趣的不是“De-Time 包本身”，而是：

> 你是否提出并验证了一个更普遍的、能改变科学建模实践的结构性观点。

软件可以是这件事的 backbone，但软件本身不是 paper 的重心。

### (3) 目前的软件证据仍然过于 software-track，缺少 NMI 级 cross-domain scientific narrative

你的 Dec-SR 稿子已经在往这个方向走，但还需要：

- 更强的跨领域案例
- 更清楚的 failure envelope
- 更严格的 counterfactual（例如 C0/C1/C2）
- 更稳健的机制性解释

如果这些成立，**软件应当作为 supporting infrastructure 出现，而不是主角**。

## 3.3 如果非要走 NMI 路线，正确打法是什么

### 不要投稿对象：De-Time 软件本体
### 更可行对象：基于 De-Time 的科学命题

更合理的 NMI 叙事是：

1. decomposition is a mechanism-identifiable operator under controlled regimes
2. continuous feature decoupling changes symbolic search geometry
3. decomposition-first pipelines improve interpretable scientific discovery under bounded compute
4. De-Time / TSSR-Bench 是 supporting artifact，而不是论文主贡献

## 3.4 NMI verdict

- **对软件本体**：reject
- **对“benchmark + Dec-SR + scientific claim”整合稿**：有潜力，但需要比当前更强的实证与边界陈述

---

## 4. 角色四：假扮 JMLR MLOSS 审稿人

## 4.1 这轮相较上一轮，分数确实上涨了

如果按 JMLR MLOSS 的视角，我会承认：

- 安装文档更诚实
- package identity 更清楚
- docs 更像真正软件
- CI/coverage/wheels 更像可审对象
- related software 更像做过功课
- compatibility layer 与 CMake/pyproject 的一致性比之前强得多

所以现在不再是“因为软件边界一团糟而 reject”。  
现在的问题变成：

> **这个软件是否已经成熟到足以作为“同行评审的软件贡献”被接收？**

我的答案仍然是：**还差一步。**

## 4.2 我会给的 major concerns

### Major concern 1 — 还没有真正 release

JMLR reviewer 会很自然地问：

- 你让我审的到底是哪一个可复现的软件版本？
- 为什么没有 tag / GitHub release / PyPI publication？
- 如果软件还没首发，active user community 证据从哪里来？

现在的 repo 明确写了 0.1.0 只是 reviewed snapshot，而不是正式 release。  
这很诚实，但也意味着软件仍停留在“准备发布”阶段。

### Major concern 2 — active user community 证据还是几乎没有

JMLR MLOSS 明确要求在 cover letter 中展示 active user community。  
目前公开仓库仍是：

- 0 stars
- 0 forks
- 0 issues
- 0 PRs

这件事你很难靠文案绕过去。

### Major concern 3 — reviewer-facing 文件仍不完全一致

最典型的两个文件：

- `JMLR_MLOSS_CHECKLIST.md`
- `JMLR_SOFTWARE_IMPROVEMENTS.md`

都还残留旧身份与旧方法边界。  
这会削弱 reviewer 对“软件边界已经稳定”的信心。

### Major concern 4 — 比较还不够“审稿级”

你已经把 `PySDKit` / `SSALib` / `sktime` 纳入比较页面，这很好。  
但对 JMLR reviewer 来说，仍然需要更强的比较证据：

- feature matrix
- runtime comparison
- memory or artifact comparison（可选）
- maturity transparency
- 你的强项到底在哪一轴，而不是泛泛地“统一 API”

当前 comparisons 页面已经比上一轮好，但仍偏“合理自述”，还没完全到“审稿压服”。

### Major concern 5 — coverage story 仍然偏 selective

虽然 `.coveragerc` 现在有 `fail_under = 90`，这是实质性进步。  
但你也明确 omit 了很多 wrapper / CLI / I/O / visualization / 若干 method files。  
这本身不违规，但你需要把这件事在 paper 或 docs 里说清楚：

- 90% 覆盖率到底覆盖的是哪一层？
- 是 core-plus-flagship surface，还是整个 package？

如果不讲清楚，reviewer 会觉得你在把“选择性 coverage”包装成全局成熟度。

## 4.3 JMLR verdict

### 当前判断

**borderline weak reject / major revision**

### 不是 reject 的原因

- 软件边界比上一轮清楚很多
- 文档、CI、wheel、coverage gate 都在
- 公开 install 路径诚实
- software identity 基本成立
- related software 已开始正面对手

### 仍然不接收的原因

- 无正式 release
- 无 adoption/community evidence
- reviewer-facing docs 仍有 stale contradictions
- 对比证据还不够硬
- benchmark residue 尚未完全从公开软件叙事中清出

---

## 5. “今年后续 vibe coding / agentic development”语境下：它到底算不算 agent friendly？

## 5.1 我的短结论

**算，但只算第一代。**

更准确地说：

> **De-Time 现在是 agent-legible / agent-usable，  
>  但还不是 2026 语境下真正的 agent-native decomposition software。**

## 5.2 为什么我认为它“确实不是假 agent-friendly”

### 已经做对的点

**(a) 你有机器可读 manifest**

`AGENT_MANIFEST.json` 已经把：

- distribution name
- preferred runtime package
- stable entrypoints
- best-first methods
- artifact contract
- legacy entrypoints

压成一个小而稳定的机器可读对象。  
这比大量仓库只写一堆 README 文案强很多。

**(b) 你有明确 input contract**

`AGENT_INPUT_CONTRACT.md` 已经清楚规定：

- 1D/2D 输入怎么路由
- period 如何传
- backend / speed_mode 如何选
- 输出应解释为哪些 artifacts
- downstream agent 如何消费 meta

这说明你在认真把“如何被代理调用”当作设计问题。

**(c) 你有短入口文档**

`START_HERE.md` / `ENTRYPOINTS.md` 是对 agent 和 Codex 很友好的。  
因为代理最怕“几十个路径，不知从哪里开始”。

**(d) 你的 artifact contract 是稳定的**

`*_components.csv`  
`*_meta.json`  
`*_components_3d.npz`

这对于 agent workflow 极重要，因为代理需要 predictable outputs。

## 5.3 为什么它还不够 2026 agent-native

### 问题 1：没有标准协议层

现在的 agent 友好，主要是“自定义文件约定”。  
但 2026 年的 agent 工具链越来越围绕：

- MCP server
- MCP registry
- registry-discoverable tools
- schemaed tool I/O
- fine-grained toolsets / allowlists

来组织。

De-Time 目前**没有 MCP server，没有 registry 条目，也没有标准化 tool schema endpoint**。  
所以它能被代理使用，但需要“看文档再自己拼”，而不是“被标准 agent runtime 原生发现和调用”。

### 问题 2：没有 token-aware interface slicing

真正 agent-native 的工具，不只要能调用，还要：

- 能输出 metadata-only
- 能 summary-only
- 能 top-k components only
- 能只返回 schema，不返回大数组
- 能基于 toolset 收窄上下文

De-Time 目前虽然有稳定 artifact contract，但还没有很好地提供：

- 极简 JSON mode
- structured summary mode
- schema introspection
- component-level selective return

所以它“能用”，但不算“省 token”。

### 问题 3：没有 toolset discipline

2026 agent 生态的一个关键经验是：

> 工具太多、描述太长、能力边界不清，会显著增加模型的 tool-selection 成本。

De-Time 现在虽然入口比之前少，但还没有把能力进一步压成：

- `decompose_univariate`
- `decompose_multivariate`
- `recommend_method`
- `profile_method`
- `explain_failure`

这种 agent-friendly small toolset。

它仍然更像一个人类包 + CLI，而不是一个 carefully curated agent tool surface。

## 5.4 我对“省 token”这件事的判断

### 现在已经省 token 的地方

- 入口少
- contract 稳定
- method first-choice 写得清楚
- artifact naming predictable

### 现在不省 token 的地方

- 仍需要代理读较多 README/docs 才能理解方法差异
- 缺少 machine-readable schemas
- 缺少 “recommend then run” 的两阶段最小接口
- 缺少 metadata-first 返回模式
- multivariate / component stack 输出可能过大

### 我的结论

**当前 De-Time 对 agent 是“可解析、可上手、可批处理”的；  
但距离“低 token 成本、低歧义、低 tool-selection 负担”的成熟 agent-native 软件，还有一整层协议化工作要做。**

---

## 6. 我对“下一代时间序列分解软件”的预测

我认为下一代真正有竞争力的时间序列分解软件，不会只是“更多方法 + 更快实现”，而会长成下面这个样子。

## 6.1 核心形态：不是方法库，而是 decomposition operating layer

下一代软件的核心不是“method zoo”，而是：

- 一个统一的 decomposition object model
- 一套 regime-aware method selection logic
- 一个 failure-diagnosis layer
- 一条 downstream integration path

也就是：

> decomposition software = algorithm wrappers + method recommender + diagnostics + downstream bridges

## 6.2 必须具备的六个能力

### (1) regime awareness

软件要能告诉用户：

- 当前更像 stationary seasonality 还是 frequency drift
- 是否存在 regime switch / change point
- fixed-period prior 是否危险
- 推荐先试 STL/MSTL 还是 SSA/EMD/Wavelet/VMD

### (2) uncertainty / failure visibility

输出不应该只有 `trend/season/residual`，还应有：

- decomposition confidence
- phase instability flags
- spectral mismatch indicators
- component leakage warnings
- backend provenance

### (3) unknown-period + change-point 能力

你 benchmark 稿子自己已经把这件事留成 future work。  
下一代软件必须把它做进公共能力层，而不是只在 paper 里承认没做。

### (4) downstream-science hooks

分解软件不应只服务可视化，还应直接服务：

- symbolic regression
- forecasting priors
- anomaly detection
- representation learning
- causal/structural hypothesis generation

### (5) agent-native interoperability

要有：

- MCP server
- registry-discoverable endpoints
- JSON schema
- toolsets / allowlists
- summary/meta-only modes
- stable minimal prompts/contracts

### (6) benchmark-backed capability maps

软件不再只说“支持方法 X”，而应给出：

- 在哪些 regime 下它通常靠谱
- 在哪些 regime 下会失败
- failure modes 的 benchmark evidence
- 与同类软件的 feature/runtime/adoption/maturity 对照

---

## 7. De-Time 离这个“下一代形态”有多近？

我会给一个比较保守的评分：

## 7.1 我给 De-Time 的当前位置

### A. 统一 decomposition contract：**8/10**
这一项已经是强项。

### B. workflow + CLI + profiling：**7.5/10**
已经够用，而且比很多只会 notebook 的仓库成熟。

### C. packaging / release maturity：**5/10**
结构修好了，但正式 release 还没落地。

### D. related-software differentiation：**6.5/10**
比上一轮明显进步，但还需要更硬的比较证据。

### E. benchmark-backed capability mapping：**6/10**
你的研究稿子已经很强，但它还没有完全沉淀进主软件叙事与公共 docs。

### F. agent-friendly / token-aware：**6/10**
已经是第一代 agent-friendly；离 agent-native 还有协议层工作。

### G. next-gen decomposition readiness：**6.5/10**
方向是对的，尤其你还有 benchmark 和 Dec-SR 两条研究线；但软件本体还没把这些能力整合成产品级 story。

## 7.2 我的总体判断

> **De-Time 已经部分符合我对“下一代分解软件”的预期，  
>  但目前更像是“下一代软件的骨架”，还不是“下一代软件的完成体”。**

它最像的不是一个终态产品，而是一条**很有潜力的研究软件路线**：

- De-Time：workflow substrate
- de-time-bench：capability map / benchmark
- Dec-SR / downstream workflows：scientific-discovery bridge
- future MCP layer：agent-native interface

如果你把这四层真正打通，它会比“一个统一分解包”强很多。

---

## 8. 我最建议你立刻做的事（按优先级排序）

## P0：立刻修，不修会继续被 reviewer 抓

1. **发布真实 release**
   - 建 tag
   - 建 GitHub release
   - 发布到 PyPI `de-time`
   - 让 install path 从 GitHub URL 过渡到正常 distribution story

2. **把 stale reviewer files 全部统一**
   - `JMLR_MLOSS_CHECKLIST.md`
   - `JMLR_SOFTWARE_IMPROVEMENTS.md`
   - 任何还把 `DR_TS_REG` 当 retained core method 的文档

3. **清理残余 benchmark 引导**
   - `docs/examples.md` 中的 leaderboard/benchmark heatmap 条目
   - `visual_leaderboard_walkthrough.py` 若不属于主包，应移动到 `de-time-bench`

4. **把 companion benchmark repo 变成可核验对象**
   - 给出公开 URL
   - 在 README / docs 中明确 split boundary
   - 说明 main package 与 benchmark repo 的接口关系

## P1：JMLR software track 真正会加分的项

5. **补一张更硬的 software comparison table**
   直接对 `statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, `SSALib`, `sktime(VMD)` 比：
   - scope
   - common result contract
   - batch CLI
   - profiling path
   - multivariate support
   - native kernels
   - maturity labeling
   - release/publication state

6. **把 local performance snapshot 变成更规范的 evidence**
   - 明确平台
   - 明确数据长度
   - 明确 repetitions
   - 最好再加 Linux 或 macOS
   - 不要只给单机单环境 anecdote

7. **解释 coverage boundary**
   - 90% 覆盖的是 core-plus-flagship，不是全包
   - 哪些 wrapper/CLI/viz 被排除，为什么

## P2：把软件从“可用”推到“下一代”

8. **增加 regime-aware recommender**
   - 输入 series metadata / pilot stats
   - 输出 first-choice methods + rationale

9. **增加 decomposition diagnostics**
   - phase instability
   - spectral leakage
   - component mismatch summaries

10. **做 MCP / agent-native 层**
   - registry-discoverable
   - small toolsets
   - machine-readable schemas
   - summary/meta-only returns

---

## 9. 最终 verdict（四角色汇总）

| 角色 | 结论 |
|---|---|
| 机器学习专家 | 有价值的软件基础设施，但 novelty 主要在 workflow layer，不是方法学突破 |
| 时间序列工程师 | 架构已经像软件包了，但 release、残余一致性、成熟度证据仍需补强 |
| Nature Machine Intelligence 审稿人 | reject（软件本体不够；应转为 benchmark + Dec-SR + scientific claim 的综合故事） |
| JMLR MLOSS 审稿人 | borderline weak reject / major revision（已经接近可审区，但还没到放心接收） |

## 我的总判断

**你这轮修改是实质性进步。**  
如果上一轮的问题是“软件边界不清”，这轮的问题已经变成了“**边界基本清楚，但证据和发布还没完全到位**”。

这其实是好消息，因为说明你已经从“先把仓库救活”走到了“怎么把它投成像样的软件论文”。

但如果你问我现在能不能放心投：

- **JMLR software track**：我仍然建议先修完 P0，再投。
- **Nature Machine Intelligence**：不要拿软件本体投；要拿“De-Time + benchmark + Dec-SR 所支撑的科学命题”去构造稿子。
