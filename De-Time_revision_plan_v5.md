# De-Time 深度修改开发计划（含网页与软件包，2026-04-08）

## 总体目标

把 De-Time 从“已经大致清理好的审稿快照”推进到：

1. **JMLR MLOSS 可接收的软件对象**
2. **agent-native / token-aware 的下一代 decomposition substrate**
3. **能够服务 benchmark 与 Dec-SR 研究主线的基础设施层**

这份计划分为四层：

- A. **发布与边界层**：让软件成为真正的 released package
- B. **网页与对外叙事层**：让 public docs、repo root、paper story 一致
- C. **证据与评测层**：让 reviewer 有足够硬的比较证据
- D. **agent-native 演进层**：让它从“agent-friendly”进化到“agent-native”

---

## A. 发布与边界层（最高优先级）

## A1. 完成第一次真实 release

### 目标
把“review snapshot 0.1.0”变成真正可安装、可引用、可复现的软件 release。

### 需要完成的动作

1. 创建正式 tag（如 `de-time-v0.1.0`）
2. 创建 GitHub Release
3. 触发 wheel/sdist 构建与发布
4. 真正发布到 PyPI `de-time`
5. 验证：
   - `pip install de-time`
   - `import detime`
   - `import tsdecomp`
   - `python -m detime version`
   - `python -m tsdecomp version`

### 为什么必须先做
如果没有正式 release：

- JMLR reviewer 会质疑你审的到底是哪一个版本
- active user / installability / citation 都难成立
- agent workflows 也很难做到稳定 bootstrap

### 验收标准

- GitHub Releases 页面不再是空白
- Tags 页面存在 `de-time-v*`
- PyPI `de-time` 可访问
- docs/install.md 可以从 GitHub URL 安装路径升级为正常 PyPI 路径
- README 中“reviewed snapshot”措辞切换为真实 release 文案

---

## A2. 固化 package boundary

### 目标
确保“主包 De-Time”和“benchmark companion repo”之间的边界不再含混。

### 当前问题
你已经在 README / PUBLISHING / pyproject / CMake 上把边界大致理顺了，但还有两个残余问题：

1. reviewer-facing 文档仍残留旧 scope
2. repo 内仍有 benchmark residue（例如 `docs/examples.md` 中的 leaderboard/benchmark 引导）

### 修改要求

#### 软件包内必须保留
- `src/detime/**`
- `src/tsdecomp/{__init__,__main__,_compat,cli}.py`
- tests/docs/examples 中与主软件直接相关的内容
- AGENT manifest / entrypoint docs（若决定保留）

#### 软件包内不应再出现为主卖点的内容
- leaderboard orchestration
- benchmark heatmap walkthrough
- benchmark-derived methods
- benchmark scenario docs 作为主包主入口

#### companion benchmark repo 中应承接
- benchmark scenarios
- synthetic generator orchestration
- leaderboard / aggregate heatmaps
- benchmark-derived methods
- benchmark paper reproduction logic

### 验收标准

- README 的“companion benchmark repo”链接可直接访问
- 主包 docs 中不再把 benchmark 可视化当作 package 功能展示
- examples 中不再默认推荐 benchmark walkthrough
- reviewer 快速浏览根目录时，不会误判这是 benchmark repo

---

## A3. 统一 reviewer-facing 文档

### 目标
消除所有仍可能让审稿人怀疑“你到底是 De-Time 还是 tsdecomp”的文件。

### 必改文件

1. `JMLR_MLOSS_CHECKLIST.md`
2. `JMLR_SOFTWARE_IMPROVEMENTS.md`
3. `JMLR_SUBMISSION_CHECKLIST.md`
4. `PUBLISHING.md`
5. `README.md`

### 必须统一的事实

- canonical identity = De-Time / `de-time` / `detime`
- `tsdecomp` 只是 compatibility alias
- retained flagship methods = `SSA`, `STD`, `STDR`, `MSSA`
- `DR_TS_REG`, `DR_TS_AE`, `SL_LIB` 不在主包
- benchmark residue 已转移到 companion repo
- 当前 comparison story 应围绕 time-series decomposition workflow layer，而不是 benchmark artifact

### 验收标准

任意两份 reviewer-facing 文档之间都不应再出现：

- 方法边界冲突
- retained/removed 方法冲突
- 包名冲突
- scope 冲突

---

## B. 网页与对外叙事层

## B1. 主页叙事收口：从“方法集合”改为“workflow substrate”

### 当前优点
主页已经明确说：

- 不是新算法
- 不是 benchmark leaderboard package
- 不是替代所有 specialized upstream library

这很好。

### 还需要进一步收口
主页和 `why.md` / `architecture.md` / `comparisons.md` 应该统一强调：

> De-Time 是一个 workflow-oriented decomposition substrate  
> for reproducible component extraction, downstream ML workflows,  
> and future scientific-discovery pipelines.

### 建议主页信息架构

1. **一句定位**
   - one stable software surface for reproducible decomposition workflows

2. **三个 strongest claims**
   - common config/result contract
   - cross-family workflow surface
   - selected native-backed flagship methods

3. **三个 explicit non-goals**
   - not a new algorithm
   - not benchmark leaderboard software
   - not deeper than every specialist library

4. **一个未来方向**
   - benchmark-backed capability maps and downstream structure discovery

---

## B2. 文档站需要再做一次“去残留”清理

### 目标
主文档站只承载“主包用户需要看到的内容”。

### 应保留在主导航的内容
- Install
- Quickstart
- Choose a Method
- ML Workflows
- Methods
- API
- Architecture
- Comparisons
- Migration
- Reproducibility
- Contributing
- Citation / Release Notes

### 应移出主包网页叙事的内容
- benchmark heatmap tutorial
- leaderboard walkthrough
- benchmark scenario gallery
- benchmark paper-specific result plots

### 具体动作

1. 清理 `docs/examples.md`
   - 删除 `visual_leaderboard_walkthrough.py`
   - 删除 “Benchmark heatmap walkthrough”
   - 删除对 `tutorials/visual-benchmark.md` 的引导
   - 如果保留该脚本，也明确标记为“belongs to companion benchmark repo”

2. 检查 `examples/`
   - 主包 examples 只保留：
     - univariate quickstart
     - multivariate workflow
     - method survey
     - profiling / CLI handoff
     - visualization tied to package usage
   - 不保留 benchmark-oriented gallery 作为主 examples

3. 在 docs 中新增一页：
   - `maturity.md` 或合并到 `methods.md`
   - 每个方法标记：
     - flagship native-backed
     - built-in Python path
     - wrapper
     - optional backend
     - experimental

### 验收标准

- 一个新用户浏览 docs 主站，不会误以为这是 benchmark 产品
- 一个 reviewer 浏览 docs 主站，会把它看成 standalone package
- 所有 examples 都能映射到主包 public surface，而不是 paper artifact

---

## B3. Comparisons 页面继续升级成“审稿级比较页”

### 当前优点
你已经把 `PySDKit`、`SSALib`、`sktime` 加入比较页，这是实质性进步。

### 仍需升级的地方
现有内容仍偏 narrative，需要更接近审稿人想看到的 software matrix。

### 推荐新增比较矩阵

| 轴 | De-Time | statsmodels | PyEMD | PyWavelets | PySDKit | SSALib | sktime(VMD path) |
|---|---|---|---|---|---|---|---|
| 核心定位 | workflow decomposition layer | classical decomposition/stat modeling | EMD family | wavelet toolkit | unified signal decomposition | SSA-only | broad TS ecosystem |
| common result object | yes | partial | no | no | partial | SSA-specific | no |
| common config object | yes | no | no | no | partial | SSA-specific | no |
| batch CLI | yes | no | no | no | no / limited | no | no |
| profiling path | yes | no | no | no | no | no | no |
| multivariate under same API | yes | limited | family-specific | transform-specific | yes | no | partial |
| native-backed retained methods | yes | upstream native internals | no | yes | mixed | yes | mixed |
| method maturity labeling | should be explicit | not applicable | family-specific | family-specific | less explicit | focused | ecosystem-level |

### 还应加的两类证据

1. **feature comparison**
2. **runtime snapshot**
   - 说明平台
   - 数据长度
   - repetitions
   - Python vs native
   - 不要只给一个轻描淡写 anecdote

---

## C. 证据与评测层（JMLR 真正会看的硬部分）

## C1. active user community 证据

### 现实
这部分目前最弱。  
如果没有 stars/forks/issues/PRs/downloads/citations，JMLR 很难轻松通过。

### 可行策略

#### 短期策略（提交前可补）
- 开至少几个真实 issue：
  - bug report
  - docs clarification
  - enhancement request
- 建一个 Discussions 或 issue template
- 若有外部同事/合作方试用，记录为：
  - external lab usage
  - internal teaching/demo use
  - reproducibility usage in companion benchmark
- 如果发布到 PyPI，收 download metrics
- 在 cover letter 里非常诚实地写：
  - public adoption still early
  - but software has public repo, docs site, CI, issue tracker, release path, and companion research usage

#### 中期策略
- 邀请一个真实外部 collaborator 提交 issue 或 small PR
- 做一次 release announcement
- 至少积累几个 installation/discussion interactions

### 注意
不要伪造社区；但要把“开放协作入口”搭出来。

---

## C2. 让 performance evidence 更像“软件证据”而不是“论文图”

### 当前问题
已有 speedup snapshot 是好的开始，但仍不足以成为 reviewer 主要依据。

### 建议最小补充包

1. `docs/performance.md` 或合并到 `comparisons.md`
2. 一个可复现脚本：
   - `python -m detime profile --method SSA ...`
   - `STD`
   - `STDR`
3. 输出：
   - Python mean / native mean
   - median
   - repetitions
   - data length
   - backend used
   - platform / Python version
4. 明确写：
   - 这是 retained flagship path 的 software validation
   - 不是通用 benchmark claim

### 更理想版本
再加一组与同类实现的对位对照：

- `STL/MSTL` vs `statsmodels`
- `EMD/CEEMDAN` vs `PyEMD`
- `SSA` vs `SSALib`（如果可公平对齐）
- `MVMD/MEMD` via `PySDKit` backend route

重点不是证明你总是更快，而是证明：

- 你在哪一类路径上有 engineering value
- 哪些路径只是统一接口，不做性能领先主张

---

## C3. coverage story 要写清楚“边界”

### 当前问题
`fail_under = 90` 是加分项，但 coverage 范围是 selective 的。

### 正确写法
不要说“whole package 91.40% coverage”。  
应该说：

> the reviewed core-plus-flagship `detime` surface is gated at 90% and the current reviewed snapshot reached 91.40%

### 需要公开写清楚
- coverage 针对的是哪一层
- 为何 omit 某些 wrappers/CLI/viz
- 为什么这仍然是合理的软件质量口径

### 验收标准
reviewer 不会因为 coverage 表述产生“你是不是在偷换概念”的疑虑。

---

## D. agent-native / token-aware 演进层

## D1. 从自定义 agent docs 升级到标准协议层

### 当前状态
你已经有：

- `AGENT_MANIFEST.json`
- `AGENT_INPUT_CONTRACT.md`
- `START_HERE.md`
- `ENTRYPOINTS.md`

这是非常好的第一代 agent support。

### 下一步应该做什么
实现一个最小可用的 **De-Time MCP server**，哪怕只提供 3–5 个工具：

1. `recommend_method`
2. `decompose_univariate`
3. `decompose_multivariate`
4. `profile_method`
5. `get_result_schema`

### 为什么这一步重要
2026 的 agent 工具生态正在向：

- MCP server
- registry discovery
- toolset allowlists
- schemaed I/O

收敛。  
如果你停留在“自定义 manifest”，会显得很快过时。

### 验收标准
- 有一个可运行的 MCP server
- 有最小工具集
- 工具 I/O 使用稳定 JSON schema
- 能被主流 agent runtime 接入

---

## D2. 真正把“省 token”做成特性，而不是副产物

### 当前短板
agent 虽然能用 De-Time，但仍缺少对 token economy 友好的输出模式。

### 建议新增 CLI / API 选项

#### 输出裁剪
- `--emit meta`
- `--emit summary`
- `--emit full`
- `--fields trend,season`
- `--top-k-components 3`

#### 结构化简报
- `detime explain`
  - 输入 series + config
  - 输出 5–10 行诊断摘要
- `detime recommend-method`
  - 输入 series stats / known period / shape
  - 输出最小推荐 JSON

#### schema introspection
- `detime schema config`
- `detime schema result`

#### metadata-first contracts
- 在 `*_meta.json` 中固定包含：
  - `result_layout`
  - `n_channels`
  - `channel_names`
  - `backend_used`
  - `method_family`
  - `maturity_level`
  - `period_assumption`
  - `failure_warnings`

### 为什么这会变成核心竞争力
下一代 agent 使用软件时，真正稀缺的不是功能，而是：

- 低歧义
- 低上下文成本
- 可预期
- 可裁剪

---

## E. 与你两条研究主线的对齐建议

## E1. 与 decomposition benchmark 稿子的对齐

你的 benchmark 稿子已经把 decomposition 解释为：

- standalone component-recovery task
- failure-mode diagnosis
- method prior vs regime compatibility
- decompose-then-regress bridge

### 软件上应该对应补的能力
1. regime labels / method recommender
2. component-quality diagnostics
3. benchmark companion repo
4. capability maps as docs or machine-readable metadata

### 软件定位建议
De-Time 主包不负责 benchmark orchestration，  
但应负责：
- public result contract
- reusable decomposition front-end
- profiling / artifact exports
- downstream bridges

---

## E2. 与 Dec-SR 稿子的对齐

Dec-SR 稿子已经把 decomposition 视为：

- continuous feature decoupling
- symbolic search precondition
- modular operator chain

### 软件层建议
为 De-Time 新增可选“downstream bridge”目录或 companion package：
- seasonal frequency proposal
- component export for symbolic regression
- direct handoff schemas to PySR / ND2 / future backends

### 但注意
这部分不要污染主包主叙事。  
可以作为：
- `de-time-bench`
- `de-time-sr`
- 或 `examples/ml/dec_sr_handoff.py`

来承接。

---

## F. 我对提交策略的建议

## F1. JMLR software track

### 现在不建议立即投
因为最核心的几个 reviewer blocker 还在：

- 无真实 release
- 无 adoption/community evidence
- stale reviewer docs
- docs/examples 中仍有 benchmark residue
- companion benchmark split 尚未完全落地

### 建议提交条件（必须满足）
1. 有 tag / GitHub release / PyPI
2. stale JMLR docs 全部更新
3. examples/docs 不再把 benchmark residue 暴露成主包功能
4. companion benchmark repo 可公开核验
5. comparisons page 更审稿级
6. cover letter 对 active user community 问题给出诚实、可验证的描述

---

## F2. Nature Machine Intelligence

### 不要拿软件本体投
软件不是主角。

### 更可能成功的对象
- decomposition benchmark + component recovery
- Dec-SR + structure discovery
- decomposition as mechanistic operator
- De-Time 作为 supporting software artifact

### 换句话说
**NMI 的主叙事是科学命题，De-Time 是基础设施；  
JMLR 的主叙事才是软件本体。**

---

## G. 最终里程碑定义

## M1 — “JMLR-ready”
满足以下条件即视为达到 JMLR 重投阈值：

- [ ] GitHub release 存在
- [ ] PyPI `de-time` 可安装
- [ ] `JMLR_*` 文档完全一致
- [ ] docs/examples 去除 benchmark residue
- [ ] companion benchmark repo 可访问
- [ ] comparisons page 含 PySDKit / SSALib / sktime 的审稿级矩阵
- [ ] performance evidence 可复现
- [ ] coverage 边界写清楚
- [ ] issue tracker / external usage / download / release evidence 至少有一部分成立

## M2 — “agent-native v1”
满足以下条件即视为达到 agent-native 第一版：

- [ ] MCP server 存在
- [ ] 3–5 个最小工具
- [ ] config/result JSON schema
- [ ] metadata-only / summary-only 模式
- [ ] toolset slicing
- [ ] registry-ready description

## M3 — “next-gen decomposition platform”
满足以下条件即视为真正走向下一代软件：

- [ ] regime-aware recommender
- [ ] decomposition failure diagnostics
- [ ] unknown-period / change-point 路线图与初版实现
- [ ] downstream discovery bridge（如 Dec-SR handoff）
- [ ] benchmark-backed capability maps

---

## 总结

你这轮已经完成了最难的一步：**把 De-Time 从“概念上独立”推进到“构建与文档上基本独立”。**

下一步不再是大修框架，而是做三件更实的事：

1. **把 release 做真**
2. **把 reviewer-facing 一致性做严**
3. **把 agent-native / next-gen 路线做成标准化层，而不是零散约定**

只要这三件事完成，De-Time 的位置会从“不错的软件包”上升到“有明确方法学前景的软件基础设施”。
