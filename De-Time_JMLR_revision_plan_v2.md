# De-Time：JMLR software track 重新审稿（恶评版）与修改开发计划
**审稿视角**：JMLR MLOSS / software track，偏苛刻、边界意识强、对“只是把 artifact 包装成 package”极其敏感。  
**评审日期**：2026-04-04  
**当前结论**：**仍然偏 weak reject / revise-and-resubmit，不建议现在就投。**

---

## 0. 核心结论

### 0.1 这次确实比上一轮更像一个软件论文候选了
本轮公开仓库比上一轮有明确进步：

- 品牌层面开始统一到 **De-Time**，README、Quickstart、Install 页面都明确写了 distribution 名称 `de-time`，推荐 import 为 `detime`，并将 `tsdecomp` 说成 legacy 兼容路径。
- 文档站已经形成完整骨架：主页、Quickstart、Install、Methods Atlas、API、Examples、Scenarios、Research Positioning、Project Status。
- 仓库已经有跨平台 CI / docs workflow / wheels workflow，且 wheels smoke test 会检查 `python -m detime --help` 和 `python -m tsdecomp --help`。
- Methods Atlas 比较诚实，明确区分 native-backed flagship、built-in、stable wrapper、experimental/optional backend。
- submission 目录新增了 JMLR checklist / improvements 文档，说明你已经开始按 software track 的语言来组织材料。

这些都是真进步，不是“包装性修辞”。

### 0.2 但从 JMLR MLOSS 的评审口径看，仍有 4 个阻断项
**最强的四个阻断项：**

1. **公开安装路径当前不可用**：文档写 `pip install de-time`，但当前 PyPI `de-time` 页面是 404。  
2. **`detime` 仍不是 canonical implementation**：`src/detime/__init__.py` 仍明确写自己是 “thin compatibility-first shim over the legacy `tsdecomp` implementation”。  
3. **网页和包边界仍混有 benchmark / agent / review artifact 痕迹**：主页、API、Examples、Scenarios、导航都还在公开暴露 leaderboard / heatmaps / agent tools / benchmark-style 页面与命令。  
4. **同类比较仍不够硬，尤其没有正面对上 PySDKit / SSALib，而且 VMD 相关比较仍停留在 `vmdpy` 而非 `sktime` 的当前维护现实。**

只要这 4 条还在，苛刻 reviewer 很容易把稿子定性为：  
**“一个认真整理过的研究 artifact，尚未完全完成独立软件身份的剥离与证明。”**

---

## 1. 站在 mean reviewer 角度，我会怎么下判断

### 1.1 当前建议
**倾向：weak reject / revise-and-resubmit**

### 1.2 不是因为“软件没做出来”，而是因为“软件身份仍没站稳”
JMLR MLOSS 真正在审的不是“你有没有代码”，而是：

- 这是不是一个**独立、清晰、可复用、可维护**的软件贡献；
- 相比已有软件，它是否带来了**significant progress**（功能、可维护性、统一接口、性能、复现性、文档、生态意义等）；
- 它是否已经形成至少**初步可见的用户/使用证据**；
- reviewer-facing artifact 是否足够 clean，而不是混着 benchmark leftovers。

De-Time 目前最尴尬的地方是：  
**你已经开始用 standalone software 的语言写故事，但代码和公开网页仍在不断泄露“我是从 benchmark artifact 抽出来的，而且还没完全抽干净”。**

---

## 2. 目前最危险的问题（按严重程度排序）

## 2.1 致命问题 A：安装说明当前在公开层面是坏的
### 现象
- 文档站 Quickstart / Install 页面写的是 `pip install de-time`。
- 但当前 PyPI 上 `de-time` 页面是 404。
- 与此同时，PyPI 上已经存在另一个无关项目 `detime`（Decimal Silicon Time），并且它就是 `pip install detime`。

### reviewer 会怎么想
这是最容易一眼击穿可信度的问题。  
software paper 连**公开安装路径**都不成立，会直接让 reviewer 质疑：

- release management 是否真的完成；
- 文档是否经过最基础的真实安装验证；
- 这个名字/包名/导入名设计是否经过足够严肃的发布前审查。

### 必改动作
- **二选一，立刻定：**
  1. **在正式投稿前真的把 `de-time` 发布到 PyPI/TestPyPI，并让文档安装命令可用；**
  2. **如果暂时不发布，就把 Install/Quickstart 全部改成 `pip install git+...` 或 TestPyPI 路径，并明确标注 “pre-release / submission snapshot”。**
- 同时必须新增一条 release QA：  
  在全新环境里实测 README 和 docs 里的安装命令，不能只在本地 editable install 上自我感动。

### 额外风险：命名/导入混淆
你现在选择：
- distribution: `de-time`
- preferred import: `detime`

这会和已存在的 PyPI `detime` 项目产生明显混淆。  
即便 distribution 名不同，**用户心智与 import 名仍会冲突**。  
如果未来公开发布，必须决定这是否可接受；若不可接受，最好在 0.x 阶段就改名，而不是到 reviewer 指出后再补救。

---

## 2.2 致命问题 B：`detime` 还只是 public shim，不是主实现
### 现象
当前公开代码里：

- `src/detime/__init__.py` 明确写：  
  **“De-Time public import surface. This package is a thin compatibility-first shim over the legacy `tsdecomp` implementation.”**
- `src/detime/core.py`、`registry.py`、`backends.py`、`io.py`、`profile.py`、`leaderboard.py`、`cli.py` 基本都是从 `tsdecomp` re-export / shim。
- `PUBLISHING.md` 也直接承认：当前仓库刻意保留 `src/tsdecomp/` 作为实现，`src/detime/` 只是 compatibility-first public shim。
- wheels / CI smoke test 也在同时测试 `detime` 和 `tsdecomp`。

### reviewer 会怎么想
这会直接引出一个 software track 最敏感的问题：

> 你到底提交的是 **De-Time** 这个新软件，还是 **tsdecomp** 旧实现的重命名包装层？

如果 reviewer 觉得答案是后者，就会说：
- contribution boundary 不清；
- package identity 仍处于过渡态；
- 还不到可以拿“独立软件贡献”来投 JMLR software track 的时候。

### 必改动作
- **把 `src/detime/` 变成 canonical implementation 路径。**
- `src/tsdecomp/` 只保留：
  - 最薄的 deprecated wrappers；
  - 明确的 deprecation warning；
  - 最小兼容周期说明。
- 所有 reviewer-facing 文档都改写为：
  - `detime` 是实现；
  - `tsdecomp` 是兼容别名，不是共同主身份。
- CI 改成：
  - 主测试只测 `detime`；
  - 单独一个 legacy-compat job 测 `tsdecomp`，并在文档里明确其地位下降。

**一句话：**
现在不是“你有没有兼容层”的问题，  
而是“兼容层为什么看起来比新包还像真身”。

---

## 2.3 致命问题 C：你说自己不是 benchmark artifact，但网页和包仍在不断泄露 benchmark artifact 气味
### 现象
虽然 README 已经明确写了类似 “not a benchmark artifact pretending to be a library” 的防御性表述，但公开网页与包仍有明显反证：

#### 文档导航和页面仍公开暴露：
- `Visual Benchmark Heatmaps`
- `Agent Tools`
- `Ecosystem and Research Positioning`
- `benchmark-style comparisons`
- `leaderboard` 相关 examples/tutorials

#### API 页面仍公开列出：
- `run`
- `batch`
- `eval`
- `validate`
- `run_leaderboard`
- `merge_results`
- `profile`

即使页面上写“first-class path is run/batch/profile”，  
但 reviewer 看到公开 API 还在大张旗鼓展示 `run_leaderboard` / `merge_results`，只会认为：
**benchmark stack 仍然是公开软件故事的一部分。**

#### 代码/打包层面仍带着：
- `src/synthetic_ts_bench`
- `pyproject.toml` 的 sdist include 仍把 `src/synthetic_ts_bench/**/*.py` 打进去
- `MANIFEST.in` / build materials 仍把 submission / docs / reviewer-facing 文件等大量一起打包
- `keywords` 里仍带 `benchmarking`

### reviewer 会怎么想
你的 README 在说“不是 benchmark artifact”，  
但你的 docs、nav、examples、API、sdist 在说“其实还是”。

这会形成**自我矛盾**，而苛刻 reviewer 很喜欢抓这种矛盾。

### 必改动作
#### 对网页（public docs）
- 从主导航移除：
  - `Visual Benchmark Heatmaps`
  - `Agent Tools`
  - 任何以 leaderboard / benchmark 为标题的公开页面
- 若你确实还需要这些内容：
  - 移到 `internal/`、`artifact/`、`maintainers/` 或单独文档站
  - 不要出现在 reviewer 第一层导航里

#### 对 API 页面
公开 API 只保留真正想让 JMLR 读者视为 public surface 的命令：
- `decompose`
- `DecompositionConfig`
- `DecompResult`
- `run`
- `batch`
- `profile`
- 必要的 I/O / registry / backends

把以下内容降级到内部/advanced/artifact docs：
- `eval`
- `validate`
- `run_leaderboard`
- `merge_results`

#### 对软件包 / sdist
- 从 installable package 和 sdist 中移除：
  - `src/synthetic_ts_bench`
  - submission-specific 文件
  - agent-specific 文件
  - 与 benchmark leaderboards 直接绑定的公开模块（除非你能在 paper 中强力辩护它们是软件贡献核心）
- `pyproject.toml` 里的 `benchmarking` keyword 删除。

---

## 2.4 致命问题 D：同类比较仍没有把真正危险的对手正面写清楚
### 现象
Research Positioning 当前对比对象主要是：
- statsmodels
- PyWavelets
- PyEMD
- vmdpy

但这份列表对 reviewer 来说是不够的，原因很简单：

- **PySDKit** 才是最危险的对手之一：它明确定位为 unified signal decomposition library，PyPI 已发布，README 强调统一接口，GitHub 体量和开发活跃度也明显更高。
- **SSALib** 虽然 scope 更窄，但它在 SSA 这个细分方向更深、更专、更成熟，而且明确展示 coverage、solver、Monte Carlo SSA、可视化、JOSS 发表等工程证据。
- **vmdpy** 作为 standalone 对手已经过时：其 README 明确写自 2023 年 8 月起由 `sktime` 维护与分发。继续把 `vmdpy` 当主要当前对手，会显得 related work 没更新。

### reviewer 会怎么想
这会被看作一种“挑安全对手比较”的写法。  
也就是：你只选那些能凸显自己叙事的基线，而没有正面对上真正会挑战你软件定位的包。

### 必改动作
在 paper 和 docs 里必须增加并认真比较：
- **PySDKit**
- **SSALib**
- **sktime (VmdTransformer / current VMD reality)**

并且比较方式不能只是“谁支持什么方法”。  
必须转成软件层面的 feature axes，例如：

- common result contract
- common config model
- batch CLI / reproducible runs
- multivariate under same public surface
- wrapper transparency / backend maturity labeling
- native kernels
- profiling workflow
- docs + CI + coverage + packaging maturity
- relation to benchmark artifacts / research workflow

---

## 2.5 中高风险问题 E：你对 PySDKit 的依赖关系会削弱“multivariate 是我的软件增量”这个主张
### 现象
`pyproject.toml` 里 `multivar` optional dependency 直接写的是：
- `PySDKit>=0.4.23`

Methods Atlas 也把多种 multivariate / modal 方法标记为 optional backend / wrapper / experimental。

### reviewer 会怎么想
如果 multivariate 能力的很大一部分来自外部 backend，  
而你又没有在 paper 中清楚划分：

- 哪些是你自己的 software contribution；
- 哪些是你做的 public contract / workflow orchestration；
- 哪些只是有边界标注的 wrapper integration；

那么 reviewer 会自然发问：

> 你新增的 multivariate capability，到底是软件本体贡献，还是对 PySDKit 等上游库的整合？

### 必改动作
在 paper 与 docs 中必须明确分层：
- **core native / built-in**
- **stable wrappers**
- **optional backends**
- **experimental research hooks**

并且每一层都要说明：
- 用户能期待什么稳定性；
- 哪部分是你的主要贡献；
- 哪部分只是生态整合。

Methods Atlas 已经有这个方向，但论文必须继承这套边界，而不是只在 docs 里诚实。

---

## 2.6 中高风险问题 F：coverage 在流程里存在，但 reviewer 看不到“coverage discipline”
### 现象
- CI workflow 会跑 coverage，并生成 term/xml/json/html。
- `.coveragerc` 配置了 `source = detime, tsdecomp`。
- 但公开层面看不到：
  - 明确 coverage 数值；
  - `--cov-fail-under=...` 或等效阈值；
  - coverage badge；
  - 公开说明哪些代码 intentionally excluded。
- 更尴尬的是：`.coveragerc` 里明确 omit 了 `tsdecomp/leaderboard.py`，而你公开 API/docs 又还在展示 leaderboard 相关能力。

### reviewer 会怎么想
这不是“没有 coverage”，  
而是“coverage discipline 没有被清楚公开，而且暴露出的未覆盖区域刚好还是你公开展示的 artifact-flavored 部分”。

### 必改动作
- 增加明确阈值：如 `--cov-fail-under=90` 或更高。
- 公布当前 coverage 数字（badge 或 docs/software paper 中写明）。
- 对 legacy shim 和 internal benchmark code 分开统计，避免把 coverage 叙事搅混。
- 若 leaderboard 仍公开存在，则必须纳入测试和 coverage；  
  若不想测，就别把它当 public software surface 展示。

---

## 2.7 中风险问题 G：JMLR reviewer-facing 文档仍有 identity leak
### 现象
你已经有：
- `JMLR_SOFTWARE_IMPROVEMENTS.md`
- `JMLR_SUBMISSION_CHECKLIST.md`

但 `JMLR_MLOSS_CHECKLIST.md` 当前标题仍然写着 **for `tsdecomp`**。

### reviewer 会怎么想
这会被看作：
- 身份迁移还没清干净；
- reviewer-facing 材料都还没统一命名；
- 说明你可能还没完成最后一轮 submission hygiene。

### 必改动作
- 所有 submission-facing 文档统一替换 `tsdecomp` → `De-Time` / `detime`（根据上下文）。
- 做一次 reviewer-facing grep：
  - `grep -R "tsdecomp" submission/ docs/ README*`
- 只允许保留那些**明确在讲 legacy compatibility** 的地方。

---

## 2.8 中风险问题 H：社区证据仍然几乎为零
### 现象
当前 GitHub 首页公开可见：
- 0 stars
- 0 forks
- 0 open issues
- 0 PRs
- 11 commits

### reviewer 会怎么想
JMLR MLOSS 并不要求你一定已经是超级成熟项目，  
但 cover letter 和 review criteria 明确关心 active user community / user evidence。  
当社区信号为零时，作者就必须用别的方式补回来，例如：

- 下游使用案例；
- 课题组内部多项目复用；
- 教学/实验复现中的使用证据；
- 可引用 release / archival snapshot；
- issue/discussion/usage examples；
- benchmark artifact 之外的真实工作流用户。

### 必改动作
如果当前确实还没有外部社区，**不要硬吹**。  
应改为：
- 诚实承认 adoption is early；
- 但补充**可验证的使用证据**（哪怕是 lab-internal / manuscript-internal / reproducibility workflows）；
- 说明该软件为何在 fragmented ecosystem 中具有 reusable value。

---

## 3. 与同类软件的对比：优缺点要怎么写才不会挨打

## 3.1 总体定位
De-Time 最有希望成立的定位不是：
- “我们比每个 specialized library 都更强”，也不是
- “我们方法很多所以更全面”。

**最稳的定位是：**
> 一个面向研究复现与方法比较的、workflow-oriented 的时间序列分解软件层，  
> 在碎片化 decomposition ecosystem 之上提供统一的 config/result contract、统一运行入口，以及有限但明确标注的原生加速与 multivariate 支持。

这是你唯一能既诚实又有进攻性的写法。

---

## 3.2 同类工作对比（建议写法）

| 软件 | 对方更强的地方 | De-Time 仍可主张的优势 | 你在论文里该怎么写 | reviewer 风险 |
|---|---|---|---|---|
| **statsmodels** | classical decomposition 深度高；STL/MSTL 成熟；社区与信任度远高于你 | 可跨 decomposition 家族统一结果结构与运行工作流 | 不要声称你替代 statsmodels；要说你覆盖的家族更广、workflow 更统一 | 若写成“我们更好做 seasonal decomposition”，会被打回 |
| **PyWavelets** | wavelet 方向深、性能和 API 都成熟，社区长期稳定 | 你可以把 wavelet 纳入统一 config/result/workflow 下 | 只能把它写成 ecosystem integration / unified workflow 的一部分 | 若把 wavelet depth 写成你自己的强项，会显得不诚实 |
| **PyEMD** | EMD 家族深、成熟、社区更大，包含 EEMD/CEEMDAN/JitEMD 等 | 你可以在同一软件层里把 EMD 与其他分解族并列比较 | 重点写统一实验与输出，不要写“我们是更好的 EMD 库” | 否则 reviewer 会说你只是 wrap 了别人 |
| **PySDKit** | 这是最危险的对手：统一 signal decomposition library、PyPI 已发布、体量/活跃度更强、方法谱更广 | 若你能证明自己的 result contract、CLI、profiling、time-series-centered API 更 clean，可形成差异 | 必须正面比较，不能回避；尤其要说清 multivariate/optional backend 与它的关系 | 如果继续不写它，reviewer 会觉得 related software 在躲最强对手 |
| **SSALib** | SSA 专精更深，coverage/solver/Monte Carlo SSA/JOSS 等都很能打 | 你可以主张 cross-family workflow，而不是 SSA 深度 | 必须承认在 SSA 家族深度上不如专用库 | 不承认会显得“想用 breadth 掩盖 depth 不足” |
| **vmdpy / sktime** | 现在 VMD 的维护现实在 `sktime`，不是旧 standalone `vmdpy` | 你可以说统一 workflow 下接入 VMD-family 能力 | related software 应该更新到 `sktime`，不要继续只写 `vmdpy` | 继续只写 `vmdpy` 会显得 literature/software survey 过时 |

---

## 3.3 De-Time 的真实优点（可以写）
你真正能稳住的优点，大概只有下面这些：

### (1) 统一的软件契约
- `DecompositionConfig`
- `DecompResult`
- `decompose`
- registry / backends / profile / batch

这比“方法表很长”更像软件贡献。

### (2) 对多家族 decomposition 工作流做了统一化
如果你的读者不是只做 EMD 或只做 wavelet，  
而是需要在不同分解家族之间统一跑实验、统一输出、统一 profile / batch / serialization，  
那 De-Time 的价值是成立的。

### (3) Methods Atlas 对成熟度分层比较诚实
这点要保留。  
很多软件论文的问题是把 wrapper、experimental backend 和 native implementation 混写成一类；  
你现在已经开始分层，这很重要。

### (4) 工程化基本骨架已经形成
CI、docs、wheels、submission hygiene、project status、publish guidance 这些都说明你不是只写了一个 notebook。

---

## 3.4 De-Time 的真实短板（也必须写）
### (1) 单家族深度普遍不如 specialized libraries
尤其在：
- EMD family
- wavelet family
- SSA specialized tooling

### (2) 身份迁移未完成
这不是小问题，是结构性问题。

### (3) multivariate 增量部分与外部 backend 耦合较深
这会削弱“这是我们自己的核心软件贡献”的说服力。

### (4) 公开网站和包边界尚未 clean
这会拖累 reviewer 对软件独立性的判断。

---

## 4. 怎么改：包含网页和软件包的修改开发计划

# Wave 0：立刻暂停“现在就投”的冲动
**目标**：先把最容易一票否决的公开层面问题修掉。  
**完成标准**：  
- 安装命令可用或已诚实标注为 pre-release；
- reviewer-facing 文档不再出现明显 identity leak；
- 公共站点不再首页展示 benchmark artifact 味道。

---

# Wave 1：软件包身份硬化（最高优先级）
## 4.1 让 `detime` 变成 canonical implementation
### 要改什么
- 将 `src/detime/` 变成真实实现路径，而不是纯 re-export。
- `src/tsdecomp/` 保留最小兼容层。
- 所有 public API 文档以 `detime` 为主。
- 为 `tsdecomp` 增加明确 deprecation warning 和 sunset 计划。

### 为什么必须先做
因为只要 `detime` 还是 shim，reviewer 就很难把这篇稿子看成“新软件”。

### 完成标准
- `src/detime/core.py` / `registry.py` / `cli.py` 不再只是转发；
- `tsdecomp` 只剩 wrapper + warning；
- 测试主路径和 coverage 主路径只围绕 `detime`。

---

## 4.2 清掉 installable artifact 里的 benchmark 残留
### 要改什么
- 从 `pyproject.toml` 的 sdist include 移除：
  - `src/synthetic_ts_bench/**`
  - submission-specific 文档
  - agent-specific 文档
- 重新审视 `MANIFEST.in`，把 reviewer 不需要的历史/代理/工件材料移出发行包。

### 为什么必须做
JMLR software paper 审的是软件，不是“整个研究项目仓库打包下载”。

### 完成标准
- `python -m build` 产物只包含软件运行真正需要的文件；
- reviewer 不会在 sdist 里看到明显的 benchmark artifact 目录。

---

## 4.3 重新定义 public CLI surface
### 要改什么
公开 CLI 只保留：
- `run`
- `batch`
- `profile`

其余如：
- `eval`
- `validate`
- `run_leaderboard`
- `merge_results`

要么移到 internal namespace，要么从公开文档消失。

### 为什么必须做
CLI 是 reviewer 最容易理解 package scope 的地方。  
你公开展示什么，reviewer 就会认为那是你要求被评审的软件主贡献。

### 完成标准
- `python -m detime --help` 的主帮助页不再把 benchmark 命令当一等公民；
- API docs 只展示软件核心工作流。

---

## 4.4 修正 package name / install story
### 要改什么
- 如果你打算维持 `de-time` + `import detime`：
  - 投稿前必须确保 `de-time` 可安装；
  - 在 docs 里解释 distribution name 与 import name；
  - 额外评估与现有 PyPI `detime` 项目的混淆风险。
- 如果你决定改 import 名：
  - 现在就改，不要等 reviewer 提。

### 完成标准
- 从一个空环境复制 docs 命令，安装成功；
- import 成功；
- README 和 docs 没有自相矛盾。

---

# Wave 2：网页/文档站公共边界重构（第二优先级）
## 4.5 清理文档导航
### 要改什么
从第一层公共导航中移除或降级：
- Visual Benchmark Heatmaps
- Agent Tools
- benchmark-style tutorials
- leaderboard walkthrough
- 任何以 artifact / benchmark 为中心的页面

### 推荐做法
导航分层改成：
1. Overview
2. Quickstart
3. Install
4. Core Concepts
5. Methods Atlas
6. API
7. Examples
8. Performance & Validation
9. Project Status
10. Contributing / Development

benchmark/artifact/agent 类内容：
- 放到 `Maintainers`
- 或 `Artifact appendix`
- 或单独 docs site

### 完成标准
- reviewer 打开 docs 第一屏，不会以为这是 benchmark project。

---

## 4.6 重写主页和示例页
### 主页要删掉/降级
- heatmaps、leaderboard 视觉元素
- benchmark sweep 叙事
- artifact provenance 过强的表述

### 主页要强化
- 问题定义：fragmented decomposition ecosystem
- 软件贡献：统一 config/result/workflow
- scope 边界：不是新算法，不替代 specialized libraries
- public path：run / batch / profile / API

### 完成标准
主页第一屏只讲软件，不讲 benchmark。

---

## 4.7 重写 Research Positioning
### 必须补入的对象
- PySDKit
- SSALib
- sktime（VMD 维护现实）

### 比较维度必须升级
不能只比较“支持哪些方法”，而要比较：
- workflow orientation
- result contract
- config model
- multivariate integration
- profiling / batch
- wrapper transparency
- package maturity / docs / CI / coverage
- intended use case

### 完成标准
这一页读完后，reviewer 会觉得你是在诚实地找自己的位置，而不是躲对手。

---

## 4.8 明确区分 public docs 与 maintainer / reviewer docs
### 要改什么
- `AGENT_*`
- reviewer-specific notes
- publishing internals
- artifact-internal pages

这些不应该和 public user docs 混在一层。

### 完成标准
docs site 面向用户；submission 目录面向 reviewer；两者职责清楚。

---

# Wave 3：工程证据补硬（第三优先级）
## 4.9 Coverage discipline 可视化
### 要改什么
- 增加 coverage fail-under 阈值；
- 输出公开 coverage 数值；
- 若仍保留 legacy shim，区分 core coverage 与 legacy compatibility coverage；
- 不再让公开暴露的 benchmark/leaderboard 代码逃离 coverage 而又出现在主 API/docs。

### 完成标准
reviewer 不需要翻 workflow 文件，也能知道：
- coverage roughly 多少；
- 质量门槛在哪里；
- 哪些代码不计入 coverage，以及为什么。

---

## 4.10 增加真正的软件比较证据
### 至少补两组
1. **软件层比较表**  
   对比 statsmodels / PyWavelets / PyEMD / PySDKit / SSALib / sktime
2. **性能/运行证据**  
   至少给出 native-backed methods 与 Python fallback 的比较  
   若能公平地和上游 specialized implementations 做某些对位比较更好，但不要乱比。

### 完成标准
paper 里不再只是 qualitative story，而有少量但有效的 quantitative software evidence。

---

## 4.11 发布纪律
### 要改什么
- 创建真正可引用的 release/tag；
- wheels/sdist 本地与 CI 双重验证；
- release notes 说明 canonical identity 与 deprecation policy。

### 完成标准
投稿时你能给 reviewer 一个“可下载、可安装、可引用、边界清楚”的版本，而不是活仓库快照。

---

# Wave 4：submission 材料重写（第四优先级）
## 4.12 论文叙事重写
### 正确主线
> De-Time is a workflow-oriented research software layer for reproducible time-series decomposition.

### 不要写成
- 我们提出了很多算法；
- 我们是最全面的 decomposition library；
- 我们比每个 specialized library 都强。

### 必写内容
- 不是新算法；
- 不替代专用库；
- 贡献在于统一 contract / workflow / packaging / selected native acceleration / multivariate integration；
- 与 benchmark artifact 的关系及剥离过程；
- 当前局限与非目标。

---

## 4.13 cover letter 要更像 software track，而不是 artifact 辩护书
### 要补的证据
- 当前公开 release / archive
- CI / wheels / docs / coverage
- realistic user evidence
- related software comparison
- 你为什么不是“只是 benchmark artifact 再包装”

### 完成标准
cover letter 主动解决 reviewer 的怀疑，而不是等 reviewer 来问。

---

## 4.14 reviewer-facing 文档统一命名和边界
### 要改什么
- `JMLR_MLOSS_CHECKLIST.md` 标题中的 `tsdecomp`
- 所有 submission 文件中的旧品牌遗留
- 将“我们从 artifact 抽离出来”的叙事写成“边界清理已完成”的证据，而不是“还在过渡期”的借口

---

## 5. 网站和软件包具体改动清单（按文件层面）

## 5.1 网站/文档站
优先修改这些文件：

- `mkdocs.yml`
- `docs/index.md`
- `docs/quickstart.md`
- `docs/install.md`
- `docs/api.md`
- `docs/examples/index.md`
- `docs/scenarios.md`
- `docs/research_positioning.md`（或同名页面）
- `docs/project_status.md`
- `docs/methods/*`
- 所有 benchmark / leaderboard / agent pages

### 重点动作
- 改 nav
- 改首页 hero 区
- 改安装方式
- 改 public API 范围
- 增加更强的 related software 页面
- 移除 benchmark artifact 的公开一等公民地位

---

## 5.2 软件包 / 构建 / 测试
优先修改这些文件：

- `src/detime/**`
- `src/tsdecomp/**`
- `src/synthetic_ts_bench/**`
- `pyproject.toml`
- `MANIFEST.in`
- `.coveragerc`
- `.github/workflows/ci.yml`
- `.github/workflows/wheels.yml`
- `README.md`
- `PUBLISHING.md`

### 重点动作
- `detime` canonical 化
- `tsdecomp` legacy 化
- sdist/manifest 清包
- coverage 阈值化
- install smoke test 以真实 public instructions 为准
- keywords / metadata 去 benchmark 化

---

## 5.3 submission / reviewer-facing
优先修改这些文件：

- `submission/JMLR_MLOSS_CHECKLIST.md`
- `submission/JMLR_SUBMISSION_CHECKLIST.md`
- `submission/JMLR_SOFTWARE_IMPROVEMENTS.md`
- paper draft / cover letter / README excerpt materials

### 重点动作
- 名称统一
- 对手比较升级
- 关系叙事从“抽离中”改成“已清理完成”
- 明确局限与非目标

---

## 6. 投稿前的 Go / No-Go 闸门

## No-Go（任何一条为真都不要投）
- `pip install de-time` 仍不可用，且 docs 仍这么写。
- `detime` 仍然主要是 shim，而不是主实现。
- 公共 docs 首页/导航仍在显著展示 benchmark heatmaps / agent tools / leaderboard walkthrough。
- 公开 API 仍把 `run_leaderboard` / `merge_results` 视为一等 public command。
- related software 仍未正面加入 PySDKit / SSALib / sktime。
- reviewer-facing 文档里还明显残留 `tsdecomp` 主身份。
- 你仍拿不到任何可验证安装/发布/测试/coverage 证据。

## Go（建议投稿前至少满足）
- 可安装 release 存在；
- `detime` 为 canonical implementation；
- `tsdecomp` 明确降级为 legacy alias；
- public docs clean；
- package clean；
- software comparison 有硬证据；
- paper narrative 只讲软件贡献，不讲算法神话。

---

## 7. 如果我是很 mean 的 reviewer，我会怎么写（你应该提前防）

### 可能的负面评语 1
> The submission presents a polished packaging effort, but the public package identity remains transitional: the advertised `detime` package is still a thin shim over the legacy `tsdecomp` implementation. This undermines the claim that the paper documents a clearly delimited standalone software contribution.

### 可能的负面评语 2
> The repository states that the project is not merely a benchmark artifact repackaged as a library, yet the public documentation, CLI surface, examples, and source distribution still expose benchmark- and leaderboard-oriented machinery. The software boundary is therefore not convincingly clean.

### 可能的负面评语 3
> The related-software discussion does not seriously engage with the closest ecosystem competitors, notably PySDKit and SSALib, and still frames VMD support against `vmdpy` rather than the current `sktime` maintenance reality.

### 可能的负面评语 4
> The installation story is currently not credible: the public documentation advertises `pip install de-time`, but the corresponding PyPI page is unavailable at review time.

你现在的修改目标，就是让 reviewer 没法顺畅写出这四段。

---

## 8. 最务实的执行顺序（推荐）
### 第一周
- 修 install story
- 修 `detime` / `tsdecomp` 身份
- 删 public docs 中 benchmark/agent 暴露
- 修 submission 文档命名泄漏

### 第二周
- 清 sdist / MANIFEST / package metadata
- 重写 research positioning
- 增加 PySDKit / SSALib / sktime 比较
- coverage 阈值化

### 第三周
- 补软件比较表和最小性能证据
- 完成 release / archive
- 改 paper / cover letter
- 做最终 reviewer-facing grep audit

---

## 9. 最终判断
**现在这个版本：仍不建议立即投稿。**

不是因为方向错，而是因为你已经进入一个很典型的 software-track 中后期阶段：  
**工程雏形已经够了，但“公开边界 clean 不 clean”将比“又加了几个方法”更决定成败。**

如果你先把：
1. install/release 真正打通，  
2. `detime` canonical 化，  
3. benchmark/agent/reviewer 痕迹从 public surface 清干净，  
4. 同类比较正面对上 PySDKit / SSALib / sktime，  

那么稿子的说服力会明显上一个台阶。

---

## 10. 本次评审所依据的公开证据（供你回查）
- JMLR MLOSS review criteria / checklist 说明页面  
- De-Time GitHub 仓库首页、README、`pyproject.toml`、`MANIFEST.in`  
- De-Time docs site：主页、Quickstart、Install、Methods Atlas、API、Examples、Scenarios、Project Status、Research Positioning、Agent Tools  
- `src/detime/*` 与 `PUBLISHING.md` 中关于 shim / legacy 的说明  
- GitHub Actions workflows：CI / docs / wheels  
- PyPI：`de-time`、`detime`、`PySDKit`、`EMD-signal`、`ssalib`  
- PySDKit / PyEMD / SSALib / PyWavelets / statsmodels / sktime 公开文档与仓库页面
