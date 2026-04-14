# De-Time 四角色深度审稿（JMLR software track 目标版）

版本：v6  
日期：2026-04-09

## 一、总判断

### 核心结论
如果**现在**按 JMLR MLOSS / software track 去投，我的判断是：

**结论：仍然不建议立刻投。更准确地说，是“major revision before submission”；如果现在硬投，最可能区间是 borderline weak reject / major revision”。**

这次版本已经比前几轮明显更强，原因主要有三点：

1. `detime` 现在已经基本成为真实的 canonical package surface，不再像早期那样只是 `tsdecomp` 的薄兼容壳。
2. docs / CI / wheels / release tag / GitHub release / companion benchmark split 都比之前干净。
3. “agent-friendly” 不再只是口号，已经出现了真正的 machine-facing surface：schema、catalog、recommend、summary/meta serialization、MCP server、AGENT manifest。

但它仍然有几个足以阻断 JMLR 的硬问题：

- **安装路径与公开发布状态存在事实不一致**：README / docs 宣称 `pip install de-time`，但公开 PyPI `de-time` 页面当前仍然 404；这对 software paper 是非常重的硬伤。
- **active user community 证据几乎没有**：stars/forks/issues/adoption/citations 仍极弱。
- **最危险对手 `PySDKit` 与 `SSALib` 的对位比较还不够硬**：你已经把它们纳入对比页，但仍需要更强的实证表格，而不是以定性叙述为主。
- **coverage 叙事仍有 reviewer attack surface**：93.2% gated coverage 是基于缩减后的分母，不是“整个可安装软件包接近 100% coverage”。
- **agent-friendly 还只是第一代，不是 2026 意义下真正 agent-native**：有 MCP / schema / summary，但缺少公开 registry/remote-ready story、token benchmark、tool-scope discipline、agent evals。

因此，这个版本已经从“明显不适合投”提升到了“有望被认真看，但还差几步关键补强”。

---

## 二、角色 1：机器学习专家（看科研价值）

## 2.1 结论

### 我会给出的判断
**有价值，而且不是小价值。**  
但这个价值不是“提出了新的时间序列分解算法”，而是：

- 把**时间序列分解**从零散的 family-specific 工具生态里抽出来，变成一个**统一、可比较、可复用的软件工作流层**；
- 让分解不仅服务于 forecasting / denoising，还能进入**结构恢复、符号回归、科学发现**这样的下游问题；
- 在你的 benchmark paper 和 Dec-SR paper 语境里，这个软件有潜力成为一个真正的“中间基础设施”。

### 为什么有价值
你上传的两篇稿子已经把这件事讲得比较清楚了：

- decomposition benchmark 那篇把 time-series decomposition 定义为独立的 component-recovery task，并且强调 unified interface、controlled mechanisms、method-agnostic alignment、diagnostic metrics。  
- Dec-SR 那篇把 decomposition 进一步提升为 symbolic regression 之前的结构先验，强调 continuous feature decoupling 是离散 symbolic search 的必要前提之一。

这意味着 De-Time 的最佳科学定位不是“又一个分解包”，而是：

> **一个支撑 decomposition-as-a-task 和 decomposition-first scientific discovery 的可复用软件基础层。**

## 2.2 你现在最强的科研叙事

最强叙事不是：
- “我们支持很多方法”
- “我们有 benchmark”
- “我们也能做 symbolic regression”

而是：

> **我们把 fragmented decomposition ecosystem 变成了一个可复用的统一操作层，并证明这个操作层既能支持 component-recovery benchmarking，也能支持 decomposition-first symbolic discovery。**

这个叙事的价值在于，它能把软件与两条研究线都连起来：

1. decomposition benchmark：说明软件有**评测基础设施价值**；
2. Dec-SR：说明软件有**下游科学建模价值**。

## 2.3 机器学习专家视角下的优点

### 优点 1：你抓住了一个“被低估的中间层”
大量 ML 工作把时间序列分解当 preprocessing，但很少把“分解软件层”本身当成独立对象来做得干净。  
你的 benchmark paper 明确指出 decomposition quality 过去常被“看起来合理”这种主观判断替代，这个问题本身就是一个科研切口。

### 优点 2：你把 decomposition 和 symbolic discovery 接起来了
Dec-SR 稿件最有意思的地方，不是 STL/MSTL 胜过谁，而是它把 decomposition 变成了**搜索空间几何重塑**的一部分。  
这使软件的价值不只是调用分解器，而是为后续解释型建模提供中间表示。

### 优点 3：你区分了 representation intervention 和 search intervention
Dec-SR 明确区分：
- C0：direct SR
- C1：lift-only
- C2：decomposition-first

这是一个很好的实验设计思想。它说明你的软件不只是“包装已有算法”，而是在支撑一类研究问题：**representation design 如何改变 symbolic identifiability**。

## 2.4 机器学习专家视角下的缺点

### 缺点 1：算法 novelty 很弱
如果把软件论文写成“新方法”，会立刻失分。  
你必须持续强调：

- 新意在**software abstraction and workflow unification**
- 不是在发明新的 decomposition algorithm
- benchmark / Dec-SR 是**软件 utility evidence**，不是软件论文主贡献本身

### 缺点 2：软件价值还没被外部社区验证
科学上“有道理”不等于“软件上已被接受”。  
对 JMLR 来说，外部 adoption 仍然太弱，这会让 reviewer 怀疑这是不是一个“作者自己论文链条专用工具”。

### 缺点 3：你的 scientific ecosystem 很强，但 software paper 容易被怀疑为 artifact repackaging
这是最需要防守的点。  
你的 benchmark paper、Dec-SR paper、software package 彼此之间逻辑很顺，但也会让 reviewer 问：

> 这是一个独立软件贡献，还是为两篇论文服务的 artifact extraction？

你需要在 paper 中主动回答这个问题，而不是让 reviewer 来替你回答。

## 2.5 从 ML 价值角度给你的建议

### 最稳妥写法
把 De-Time 写成：

> 一个可复用的软件中间层，连接  
> （i）decomposition-as-evaluation  
> （ii）decomposition-as-representation  
> （iii）decomposition-as-machine-tooling

### 不该写的
不要写成：
- “我们证明 decomposition 很重要，所以软件应该被接受”
- “我们 benchmark / Dec-SR 很强，所以 package 也该被接受”
- “我们覆盖很多方法，所以更有价值”

JMLR 不吃这种逻辑。  
它要的是：**这个软件本身，是否独立且显著地推进了现有软件生态。**

---

## 三、角色 2：时间序列工程师（看好不好用）

## 3.1 结论

### 工程判断
**比前几轮好用很多，但还没有到“我会无脑推荐团队上生产或长期研究工作流”的程度。**

如果我是时间序列工程师，我会说：

- 现在它已经具备“统一入口 + 统一结果对象 + 统一配置对象 + 方法推荐 + summary/meta 输出”的良好骨架；
- 但“安装可信度、成熟度边界、性能边界、依赖层级、对外发布状态”还不够稳定。

## 3.2 现在已经做对的工程事

### 1. `detime` 终于像一个真正的软件包了
这是本轮最重要的进步。  
如果 public API 仍然是 shim，工程上就不可信；现在 canonical surface 已经明显转正。

### 2. `DecompositionConfig` / `DecompResult` 是正确的抽象
这套抽象非常重要。  
对工程师来说，最大的痛点不是“有没有某个方法”，而是：

- 每个方法参数名字不同；
- 输出对象完全不同；
- 很难批量跑、很难进下游 pipeline；
- 很难让别人复现。

你现在的 config/result contract，至少把这件事做成了软件层面的公共协议。

### 3. `summary` / `meta` serialization 很实用
这不只是 agent feature。  
对工程也有价值：

- 日志输出不会爆炸；
- 批量 pipeline 可以只存 metadata；
- 下游系统可以先看 summary，再决定要不要拿 full artifact。

### 4. docs surface 比之前干净
主导航不再挂 benchmark-style 页面，这是正确方向。  
作为工程用户，我希望一进来先看到 install、quickstart、methods、API、migration、reproducibility，而不是 artifact gallery。

### 5. CI / wheels / docs / release 工作流已经接近“像一个认真维护的软件项目”
这是明显加分项。  
至少 reviewer 不会再一眼看出“这只是论文补充材料”。

## 3.3 工程视角下仍然不舒服的地方

### 1. 安装与发布状态不可信
这是现在最严重的问题。  
如果 README / docs 写了：

```bash
pip install de-time
```

但实际公开 PyPI 页面还是 404，工程师第一反应不是“快修一下”，而是：

> 我怎么知道还有哪些 public-facing claim 也没对齐？

这会直接伤害信任。

### 2. 成熟度标签虽然有，但还不够贯彻到整个 UX
你已经在方法页面区分 flagship / built-in / wrapper / optional backend，这是好事。  
但工程上还需要更明确：

- 哪些方法默认可用；
- 哪些需要额外依赖；
- 哪些只是 compatibility wrappers；
- 哪些不建议用于 large-scale batch；
- 哪些不保证 cross-platform stability。

如果这些边界没有在 CLI / docs / API reference 里反复一致体现，工程团队很容易踩坑。

### 3. coverage 口径容易引发误解
93.2% 看起来不错，但如果它只覆盖“核心安全子集”，那就不能被讲成“整个包测试很强”。  
工程上这没问题，前提是你说清楚。  
但如果 public narrative 不够清楚，reviewer 会认为你在“美化 coverage”。

### 4. 对性能的 story 还太窄
你已经有 native snapshot，这是好事。  
但工程师真正想知道的是：

- 哪些方法 native-backed；
- 对哪些输入规模有意义；
- 有无跨平台一致性；
- fallback 与 native 的 numerical agreement 如何；
- 真实 workload 下 wall-clock 是否稳定。

如果只给单机 microbenchmark，很容易被看成 demo。

### 5. 近邻竞品对位还不够工程化
工程师不会只看“支持哪些方法”，而会问：

- 为什么不用 PySDKit？
- 为什么不用 statsmodels + 自己 glue code？
- 为什么不用 SSALib + PyWavelets + PyEMD 的组合？
- 为什么不用 sktime 生态？

你现在的 docs comparisons 已经开始回答这个问题，但还缺真正能支持采购/选型的表格。

## 3.4 时间序列工程师给出的推荐级别

如果按工程推荐等级分：

- **骨架设计：A-**
- **研究工作流可用性：B+**
- **安装与发布可信度：C**
- **成熟度透明度：B**
- **大规模工程采用 readiness：B-**
- **我会不会推荐别人上手：会，但会附带警告**

### 我会附的警告
1. 先不要完全相信安装说明，先检查发布状态；
2. 只把 flagship methods 当“强支持”；
3. wrapper/optional methods 需要单独 smoke test；
4. 先用 `summary`/`meta` 模式搭 pipeline，再决定是否保存 full outputs；
5. 不要把 PyPI、coverage、agent readiness 的 public claims 写得比事实更强。

---

## 四、角色 3：JMLR MLOSS / software track 审稿人

## 4.1 结论

### 作为 JMLR software reviewer 的判断
**现在这个版本已经不再是“明显 reject”；但仍然还没有到“我愿意给 accept / weak accept”的程度。**

我大概率会给：

- **总体建议：major revision / revise before formal submission**
- 如果真现在送审：**weak reject 或 major revision 倾向**

## 4.2 这轮你已经修正了什么

我必须先承认你确实修正了几个之前最致命的问题：

### 修正 1：软件身份比以前清楚多了
过去最大问题是 `detime` 像 shim；现在这个点明显改善。  
`tsdecomp` 基本退为窄兼容层，这大幅降低了“只是换皮”的指控强度。

### 修正 2：公共网页与 installable package 的边界清理得更好了
benchmark / internal tooling 不再像以前那样溢出到主导航与包发布面。  
这对 software track 非常重要。

### 修正 3：release / tag / docs / CI / wheels 形成了更完整的软件工件链
这让你从“论文附带代码”更靠近“独立软件项目”。

### 修正 4：你开始正面对比 PySDKit / SSALib
这件事很关键。  
如果 related software 里故意回避最强近邻，reviewer 会直接不信任作者判断。

## 4.3 仍然卡住你的 major concerns

### Major concern 1：installation claim 与 public release state 不一致
这件事足以单独构成 major concern。  
JMLR MLOSS 明确要求 installation instructions、version to review、website、release quality。  
如果你在 docs/README 里把 `pip install de-time` 写成公开事实，但 PyPI 实际还没上线，这是 reviewer 一眼就能复现的硬错误。

这不是小瑕疵。  
对 software paper 来说，这相当于“最基础的用户路径不可信”。

### Major concern 2：active user community 仍然几乎没有
JMLR MLOSS 官方要求 cover letter 说明 active user community。  
你现在最难回答的问题仍然是：

- stars/forks 很少；
- issues/PR 极少；
- 外部教程/外部引用/外部项目依赖证据几乎没有。

你可以说“软件刚公开、还早期”，这是真实；但 reviewer 不会因为真实就自动放宽标准。  
它会变成一个客观弱项。

### Major concern 3：comparison to prior implementations 还不够像 JMLR 风格
JMLR reviewer 真正想看的不是“我们和谁生态定位不同”，而是：

- 功能边界差异；
- runtime / memory / install / docs / CI / API contract / batch capability；
- 在哪几个高价值 use case 下，De-Time 的确显著更好。

你现在的对比已经比之前强，但离“editor 一看就觉得应该收”仍差一步：  
还需要一张**真正 reviewer-grade 的 empirical comparison package**。

### Major concern 4：coverage 叙事仍然有被攻击的空间
JMLR 写得很明确：coverage should be close to 100%。  
你的 gated coverage 现在是 93.2%，但分母缩减明显。  
这不是不能接受，而是你必须：

- 要么把 coverage scope 扩大；
- 要么非常诚实地把“core-surface coverage”与“package-wide coverage”分开。

如果你既不扩大、也不诚实拆分，reviewer 会认为你在规避标准。

### Major concern 5：软件价值必须压在“workflow/software abstraction”上，而不是科学结果上
你现在很容易被两篇关联稿件拖偏：

- benchmark 稿件很强；
- Dec-SR 稿件也有亮点；

但 JMLR software paper 若过度依赖这些 scientific results 来证明软件价值，就会被 reviewer 反问：

> 那真正值得发表的是 scientific benchmark / Dec-SR paper，还是这个软件本身？

所以 paper 中必须清楚把 benchmark 和 Dec-SR 降格成：

> **software utility evidence**

而不是 software paper 主体本身。

## 4.4 我会怎样给评分（模拟）

以下是我会给出的近似印象分（5 分制）：

| 维度 | 分数 | 说明 |
|---|---:|---|
| 设计清晰度 | 4.0 | `config/result/registry/schema` 做得不错 |
| 文档与教程 | 4.0 | docs 已像正式软件项目 |
| 开源与工程 hygiene | 4.2 | license / CI / wheels / docs / release 都在 |
| 重要性 / significance | 3.7 | 方向值得，但仍需更硬证据 |
| 与现有软件差异化 | 3.0 | 叙事有了，实证仍不足 |
| 安装与发布可信度 | 2.0 | PyPI/public install inconsistency 是硬伤 |
| 测试与覆盖率 | 3.1 | 有体系，但 coverage claim 仍需更诚实/更强 |
| 社区采用 | 1.5 | 太弱 |
| 录用倾向 | 2.8 / 5 | 还差一轮关键修改 |

## 4.5 如果我是 reviewer，我会写的最狠一句话

> The package is now substantially cleaner and better scoped than earlier versions, and the canonical `detime` surface is a real improvement. However, the paper still does not fully prove that this is a sufficiently mature and externally validated software contribution for JMLR MLOSS. The public installation path remains inconsistent with the visible release state, external adoption evidence is minimal, and the comparison against the closest software competitors is still more qualitative than decisive.

## 4.6 什么会让 JMLR 编辑觉得“收它是对的”

编辑最想看到的不是“你很努力”，而是下面四件事同时成立：

1. **独立软件身份稳定**  
   `detime` 是 canonical；benchmark 与 paper artifact 不混入 installable core。

2. **安装、发布、复现路径真实且可复现**  
   PyPI / release / wheels / docs 完全一致，没有一句 public claim 会被 reviewer 复现打脸。

3. **与近邻软件的差异被清楚证明**  
   尤其是 PySDKit 与 SSALib；不是说“我们也做分解”，而是说“我们提供别家没有的一致工作流/机器接口/结果契约/批处理与集成能力”。

4. **软件已经超出作者本人论文链条**  
   即便 external community 仍早期，也至少要拿出更像样的 adoption proxies：下载、依赖、外部 issue、外部 notebooks、外部 mentions、教学使用、lab-internal but multi-project use evidence。

---

## 五、角色 4：2026 agent / vibe-coding / token-efficiency 审稿人

## 5.1 结论

### 我会怎么给这个维度定性
**现在的 De-Time 不是“假 agent-friendly”，而是“第一代 agent-friendly”；但它还不是 2026 意义下的 agent-native 时间序列软件。**

这是一个很重要的区分。

## 5.2 为什么它已经算 agent-friendly

### 1. 你确实有 machine-facing contract
不是只有 README 说说而已。  
现在已经能看到：

- machine-readable catalog
- schema assets
- `recommend` path
- `summary` / `meta` serialization
- MCP server
- AGENT manifest

这说明你已经理解了一个关键事实：

> LLM/agent 不应该直接吞全量 ndarray；  
> 它应该优先消费 schema、catalog、compact summaries、artifact metadata。

### 2. 你已经开始做 token-aware output design
`full / summary / meta` 这件事非常对。  
这不仅节省 token，也让 agent 更稳定。

### 3. 你在做“工具优先”而不是“prompt 优先”
这是 2026 语境里非常重要的方向。  
真正可用的 agent 软件，不是给一长串 README 让模型自己猜，而是：

- 给它稳定 tool surface
- 给它 strict schemas
- 给它 low-token inspection path
- 给它 deterministic recommend / summarize / list methods

你已经有这个雏形。

## 5.3 为什么它还不算 agent-native

### 问题 1：MCP 还是局部能力，不是完整分发故事
你现在有 MCP server，但公开信息里还看不到更强的 agent distribution story，例如：

- 是否有公开 remote MCP endpoint？
- 是否有 registry-friendly discovery metadata beyond local manifest？
- 是否有 toolset scoping / allowed-tools presets？
- 是否有 versioned machine contract guarantees？
- 是否有 hosted capability profile for agents？

如果这些缺失，它还是“本地可接”的工具，不是“生态级 agent component”。

### 问题 2：没有 token benchmark
你说 low-token，但还没有给 reviewer / editor 一个真正可引用的证据包：

- full vs summary vs meta 的 token size 对比
- single-channel vs multivariate 的 token scaling
- agent typical workflow 下上下文成本节省多少
- MCP route 相比直接 JSON dump 节省多少

如果不做这件事，“省 token”仍然只是好直觉，不是审稿可用的 claim。

### 问题 3：没有 agent eval harness
2026 的 agent-friendly 软件不该只说“可以接 agent”，而要回答：

- agent 能否稳定选到对的方法？
- 方法推荐的 top-k 是否合理？
- summary/meta 是否足够支撑后续 decision？
- agent 在 bounded context 下是否还能完成 end-to-end decomposition task？

也就是：
> 你需要 tool eval，而不只是 tool presence。

### 问题 4：还不够“tool-scope disciplined”
真正 agent-native 的系统会非常强调：
- 小而稳的工具集合
- 每个工具输出严格结构化
- progressive disclosure
- context budget control
- 失败时可恢复的错误语义

你已经部分做到，但还没有把它写成 public doctrine / measurable guarantees。

## 5.4 2026 下我对“vibe coding”真实走势的判断

### 我的判断
今年后续所谓 vibe coding，如果继续成熟，实际会向两条线分化：

1. **消费级 vibe coding**：  
   让模型“差不多写出来”，容忍隐式约定与人肉修补。

2. **研究/工程级 agentic coding**：  
   要求 schema-first、tool-first、eval-first、cost-aware、registry-aware。

JMLR 相关的软件，必须服务第二条线。  
因为研究软件最怕的不是写得慢，而是：

- 不可复现
- 不可验证
- 接口不稳定
- token/上下文不可控
- agent 用一次能成，用第二次就漂

## 5.5 从这个角度看，你的软件在哪个阶段

我会给你一个三档判断：

- **Human-usable research software**：已经达到
- **Agent-friendly research software**：已经基本达到
- **Agent-native scientific software**：还没达到

### 已达到的部分
- canonical package API
- machine-facing schema assets
- result compaction
- recommendation path
- MCP server
- artifact contract

### 还没达到的部分
- remote/discoverable MCP distribution
- token-cost benchmarks
- agent evaluation suite
- capability negotiation / tool subsets
- benchmarked machine-contract stability across versions
- richer provenance handles for large artifacts

---

## 六、下一代时间序列分解软件应该是什么样

## 6.1 我对下一代软件的预测

下一代真正强的 time-series decomposition software，应该同时满足下面 10 条：

### 1. 双接口：human API 与 machine API 对称
不是“给人看的 Python API + 给 agent 凑合用的 CLI”。  
而是：
- human-facing：易用
- machine-facing：schema-stable、contract-first、versioned

### 2. 结果对象是分层可展开的
默认不是 full array dump。  
而是：
- meta
- summary
- sampled/component preview
- full artifact by explicit request

### 3. 方法不是平铺列表，而是 capability cards
每个方法都要带：
- assumptions
- failure modes
- maturity level
- computational profile
- multivariate support
- downstream suitability

### 4. benchmark 作为 companion，不混入 installable core
这点你已经在往对的方向走。  
下一代软件必须把“library”与“benchmark artifact”彻底切开。

### 5. 需要原生支持 downstream composition
分解不应该止步于 decomposition。  
它应该自然进入：
- symbolic regression
- forecasting
- anomaly detection
- feature extraction
- causal / scientific pipelines

### 6. 需要原生支持 agent workflows
包括：
- MCP / tool contracts
- schema validation
- machine-readable catalog
- recommendation
- error semantics
- context-aware output sizing

### 7. 需要有 token-budget design
这会越来越重要。  
因为多变量长序列极容易把 agent 上下文打爆。

### 8. 需要 capability-aware recommendation
不是只说“支持哪些方法”，而是能根据输入结构与目标输出：
- 推荐方法
- 推荐参数范围
- 解释推荐依据
- 给出失败风险

### 9. 需要外显 reproducibility envelope
不是单纯提供代码，而是：
- versioned artifacts
- platform matrix
- dependency tiers
- deterministic smoke tests
- provenance metadata

### 10. 需要 external plugin / extension story
未来不可能一个包自己覆盖所有 decomposition family。  
真正可持续的软件一定要让：
- family-specific specialists
- benchmark suites
- downstream consumers
- agents
在稳定 contract 上接入。

## 6.2 De-Time 离这个“下一代形态”还有多远

### 已经符合预期的部分
- config/result contract
- summary/meta compact outputs
- recommendation / catalog
- MCP 方向
- benchmark companion split
- downstream narrative（benchmark + Dec-SR）

### 还不够的部分
- public release truthfulness
- package adoption
- complete capability cards
- token-budget evidence
- agent eval harness
- stronger plugin / extension architecture visibility
- external ecosystem trust

### 总判断
**它已经有“下一代分解软件”的轮廓，但还没有完成从 good research software 到 reference software 的跃迁。**

---

## 七、如何横向对比同类软件，才能让 JMLR 编辑觉得录用是正确选择

## 7.1 绝对不要用的对比策略

不要写成：
- “我们比 statsmodels 更全面”
- “我们比 PyWavelets / PyEMD 更统一”
- “我们支持的方法更多，所以更值得收”

这是很危险的。  
因为任何 specialist reviewer 都会反驳：

- statsmodels 在 classical decomposition 上更深；
- PyWavelets 在 wavelet 上更成熟；
- PyEMD 在 EMD family 上更成熟；
- SSALib 在 SSA 上更专业；
- PySDKit 才是最近邻竞品。

## 7.2 正确的编辑说服逻辑

正确逻辑应该是：

> **De-Time 并不试图取代 specialist libraries。**  
> **它的价值在于填补 specialist libraries 与 benchmark artifacts 之间的空白：**  
> 通过统一结果契约、统一配置模型、统一机器接口、有限但真实的 native acceleration、以及可复现工作流支持，提供一个“跨 family、跨人机接口、跨研究流程”的 decomposition software layer。

换句话说，你要卖的不是“最强方法”，而是：

> **最好的 decomposition workflow abstraction**

## 7.3 我建议你把竞品分成四组写

### A 组：classical / statistical specialists
- statsmodels
- 重点：classical seasonal-trend decomposition 深度、社区成熟度

### B 组：single-family signal specialists
- PyEMD
- PyWavelets
- SSALib
- 重点：EMD、wavelet、SSA 的家族深度与专精能力

### C 组：nearest unified competitor
- PySDKit
- 这是最重要的对手  
- 你必须正面对比，而不是轻描淡写

### D 组：ecosystem transforms / continuation projects
- sktime（尤其 VMD continuation）
- 说明你知道生态真实状态，而不是拿过时上游说事

## 7.4 你需要补的五张 reviewer-grade 表

### 表 1：Software identity / scope table
列：
- canonical package
- install path
- supported families
- unified config object
- unified result object
- batch CLI
- profiling path
- multivariate support
- machine-facing schema
- MCP / tool surface

### 表 2：Maturity / dependency table
列：
- method
- flagship / built-in / wrapper / optional
- native-backed?
- optional deps?
- tested in CI?
- docs tutorial?
- stability note?

### 表 3：Runtime / memory comparison table
只比你能公平比的内容：
- STL/MSTL vs statsmodels
- SSA vs SSALib
- EMD/CEEMDAN vs PyEMD
- wavelet path vs PyWavelets
- unified toolkit vs PySDKit（在 common tasks 上）

### 表 4：Agent-friendly comparison table
列：
- machine-readable catalog
- JSON schema assets
- compact result modes
- method recommendation
- MCP surface
- artifact contract
- token-aware summaries

这一张非常容易让编辑觉得“这不是旧式包”。

### 表 5：Reviewer trust table
列：
- public release
- PyPI/live install
- GitHub release/tag
- CI matrix
- wheels
- docs
- coverage definition
- reproducibility script
- benchmark separation

这张表会直接解决“为什么我应该信任它”的问题。

## 7.5 你对每个竞品应该怎么写

### 对 statsmodels
写法：
- 它在 classical decomposition 上更成熟、更有社区信任；
- De-Time 不替代它；
- De-Time 的贡献是把 statsmodels 风格方法与其他 family 放进统一结果/配置/机器接口中。

### 对 PyEMD / PyWavelets / SSALib
写法：
- 它们在各自家族深度上更强；
- De-Time 的目标不是超越家族深度，而是统一工作流与人机接口；
- 必须诚实承认这一点，反而更可信。

### 对 PySDKit
写法必须最硬。  
你要明确说：

- 它是最近邻 unified competitor；
- De-Time 的优势不在“也有统一接口”，而在：
  - decomposition-specific result contract
  - machine-facing schema/recommend/catalog
  - summary/meta compact outputs
  - CLI + profiling + reproducibility boundary
  - native-backed flagship methods
  - companion benchmark separation

如果你对 PySDKit 的比较还停留在抽象定位层，JMLR reviewer 不会买账。

## 7.6 一句话编辑级定位

你最值得反复坚持的一句话是：

> **De-Time should be judged not as a replacement for specialist decomposition libraries, but as a reusable workflow and machine-facing software layer that standardizes decomposition across fragmented ecosystems and enables downstream scientific use.**

---

## 八、最具体的修改优先级（按影响排序）

## P0：必须先修，不修不能投
1. **PyPI / install truthfulness**
2. README / docs / release / package metadata 完全一致
3. cover letter 中的 release state 与 public state 完全一致

## P1：JMLR 主要加分项
4. reviewer-grade related software comparison（尤其 PySDKit / SSALib）
5. 更诚实、可解释的 coverage 叙事
6. package-wide test / smoke evidence 扩展
7. adoption evidence 收集与 cover letter 写法

## P2：把“agent-friendly”变成新卖点
8. token benchmark
9. agent eval harness
10. MCP / machine contract 文档升级
11. capability cards / method cards

## P3：提升编辑信心
12. 明确把 benchmark 和 Dec-SR 写成 companion evidence
13. 在 paper 中反复强调 software abstraction 而不是 algorithmic novelty
14. 用 “workflow layer + machine-facing layer + downstream utility” 三位一体叙事

---

## 九、最终 verdict

## 9.1 如果今天就投
**不建议。**

## 9.2 如果完成下一轮关键修改后再投
**有机会进入可认真讨论的 weak accept / borderline accept 区间。**

## 9.3 我最真实的评价
现在的 De-Time 已经不是“仓促包装的论文 artifact”了。  
它开始像一个真正的软件项目，也开始显露出“下一代 decomposition software”该有的轮廓。  
但距离 JMLR software track 想要的“成熟、可信、差异化清晰、对外可安装、对比足够硬”的状态，还差最后一轮关键收口。

---

## 十、给你最短的战略建议

### 你的最佳路线不是继续“加方法”
而是：

1. **先把 public release / install / docs claim 做到 100% 对齐**
2. **再把 PySDKit / SSALib / statsmodels / PyEMD / PyWavelets / sktime 的比较做硬**
3. **再把 agent-friendly 变成你独有的新一代卖点**
4. **最后再写 paper，把 benchmark 与 Dec-SR 降为 utility evidence**

如果这四步都做到，JMLR 编辑就更容易把它理解为：

> 一个清晰、独立、值得归档的软件贡献，而不只是作者论文链条的副产物。
