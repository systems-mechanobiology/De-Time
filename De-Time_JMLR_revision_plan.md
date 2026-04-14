# De-Time 面向 JMLR MLOSS 的深度修改与开发计划

## 0. 核心结论

当前版本的 De-Time **最危险的问题不是“没有工程化”，而是“软件身份还没有清理干净”**。  
如果按 JMLR MLOSS 的审稿口径看，最容易被抓住的点有四个：

1. **canonical package 身份不清**：`detime` 仍然是 `tsdecomp` 的兼容 shim，而不是清楚的主实现。
2. **installable artifact 边界不清**：benchmark 代码、submission 文件、公共软件代码仍然混在同一可分发工件里。
3. **public docs 仍有较重 benchmark / artifact 气味**：导航与 CLI 页面还把 leaderboard、eval、merge 等暴露为公开软件表面。
4. **与同类软件相比的“显著软件进步”证据不够硬**：JMLR 明确要求比较 runtime / memory / features，并要求 active user community、强文档、接近 100% 的 coverage、跨平台 CI。

所以修改目标不能只是“润色 paper”，而必须是一次**软件边界重构 + 网站重构 + 分发工件重构 + 论文叙事重构**。

---

## 1. 证据化诊断

### 1.1 JMLR MLOSS 在审什么

JMLR MLOSS 的公开要求里，以下几点最直接相关：

- cover letter 需要说明 open-source license、project URL、reviewed version，以及 **active user community 的证据**；
- review criteria 明确要求：  
  - novelty / breadth / significance；  
  - 与既有实现相比的 **runtime / memory / features** 对比；  
  - installation instructions、tutorials、non-trivial examples、完整 API 文档；  
  - 对新开发者友好、设计清晰、developer docs 清楚；  
  - **extensive unit and integration testing**，并报告 coverage，且明确写了 **“expected that test coverage is close to 100%”**；  
  - 多平台 CI。  
- JMLR 作者说明还要求：所有 claims 必须有证据支撑；如果与既有/并行工作重叠，必须清楚交代 delta，而且 delta 不能只是小修小补。

这意味着：**你不能只说“我们是一个整理得很好的包”；你必须证明“这是一项边界清楚、独立可复用、相对已有软件有明确推进的软件贡献”。**

### 1.2 当前 package identity 的最大硬伤

仓库现在的公开状态非常容易触发审稿人的质疑：

- `src/detime/__init__.py` 明写：`detime` 是对 legacy `tsdecomp` 的 “thin compatibility-first shim”。  
- `src/detime/cli.py` 只是从 `tsdecomp.cli` 导入 `main`。  
- `tests/test_branding_imports.py` 还专门测试 `detime` 和 `tsdecomp` 两套 CLI 都正常。  
- `pyproject.toml` 同时保留 `detime` 与 `tsdecomp` 两个 script entrypoints。  
- cover letter 也明确承认：软件是从更大的 benchmark-oriented artifact 中抽出来的，且 public adoption 仍然早期。  
- draft paper 继续承认 preferred import 是 `detime`，但 legacy `tsdecomp` 仍保留。

这会让 reviewer 立刻追问：

- 你投稿的到底是 `detime` 还是 `tsdecomp`？
- `detime` 是真正的软件，还是一个 rebranding 层？
- 你提交的是“新软件”，还是“旧 artifact 的包装升级版”？

**这是当前第一优先级的 blocker。**

### 1.3 installable artifact 仍然混入 benchmark residue

这不是抽象判断，而是分发边界层面的真实问题：

- `src` 目录里不只有 `detime` 和 `tsdecomp`，还包含 `src/synthetic_ts_bench`。
- `pyproject.toml` 的 source distribution include 里，明确还打包：
  - `src/synthetic_ts_bench/**/*.py`
  - `JMLR_SOFTWARE_IMPROVEMENTS.md`
  - `JMLR_MLOSS_CHECKLIST.md`
  - 多个 submission / agent / publishing 文件
- draft paper 也承认 earlier code lived inside broader benchmark artifact，并且软件稿要强调“不是 benchmark-results paper”。

如果 reviewer 下载源码归档包，看到 benchmark code、submission notes、agent files、public package source 同时出现，最直观的感受就是：

> 这不是一个边界稳定的软件 release，而是一个“为投稿整理过的研究仓库”。

对 MLOSS 来说，这是非常危险的信号。

### 1.4 public docs 仍有过强的 benchmark-facing 公开表面

当前 docs 站的导航与公开页面也会放大同样的问题：

- `mkdocs.yml` 顶层 nav 里公开放着：
  - `Visual Benchmark Heatmaps`
  - `Agent Tools`
  - `Project Files and Citation`
- `docs/api.md` 把 CLI 暴露为：
  - `run`
  - `batch`
  - `eval`
  - `validate`
  - `run_leaderboard`
  - `merge_results`
  - `profile`
- 同一页还明确说 first-class path 是 `run / batch / profile`，这相当于自己承认其余几个命令不是核心用户路径。
- `docs/tutorials/visual-benchmark.md` 直接讲 “lightweight leaderboard heatmaps”，并解释 full benchmark stack 更 heavy、更 research-artifact flavored。

这就会形成一个很尴尬的审稿体验：  
**文档一边说“这是 standalone software”，一边又在顶层公开展示 benchmark 风格的页面和命令。**

### 1.5 正面资产：你不是没东西

当前版本并非没有实质软件贡献。实际上，有几项东西是可以保住并强化的：

#### A. 公共结果契约是清楚的
`DecompResult` 统一包含：

- `trend`
- `season`
- `residual`
- `components`
- `meta`

`DecompositionConfig` 也已经把方法名、参数、backend、speed mode、profiling、device、channel names 等统一起来。  
这是明确的软件设计贡献，不只是 README 文字。

#### B. 单一 `decompose(...)` 入口能处理 univariate / multivariate / channelwise
`registry.py` 里有：

- `InputMode = "univariate" | "multivariate" | "channelwise"`
- 输入归一化
- 输入模式验证
- result layout annotation

这说明“一个统一 public interface + 一个统一 result model”不是空话。

#### C. Methods Atlas 的成熟度边界写得很诚实
`docs/methods.md` 明确区分：

- native-backed flagship：`STD`, `STDR`, `SSA`
- built-in flagship：`MSSA`
- stable wrappers：`STL`, `MSTL`, `ROBUST_STL`
- wrapper / experimental：`EMD`, `CEEMDAN`, `VMD`, `MVMD`, `MEMD`
- benchmark-support wrappers：`DR_TS_AE`, `SL_LIB`

这类“成熟度分层”是对的，而且应当进一步强化，而不是弱化。

#### D. 工程基础已经有雏形
当前已有：

- BSD 3-Clause license
- GitHub docs site
- CI（Linux/macOS/Windows；Python 3.10/3.12）
- coverage report job
- docs build job
- wheel build workflow
- contributor / security / roadmap / citation 文件

所以问题不是“要从零开始工程化”，而是**要把已有工程资产重排成 JMLR 能接受的软件故事**。

### 1.6 目前最强的外部竞争对手是谁

对于 JMLR software track，竞争不是“谁算法更多”，而是谁的软件定位更清晰。

#### `statsmodels`
优点是 classical decomposition（如 STL/MSTL）很成熟；  
De-Time 不能宣称自己在 classical decomposition 上比它更强，只能说自己提供 cross-family workflow 层。

#### `PyEMD`
EMD / EEMD / CEEMDAN 家族深度强，社区规模明显更大；  
De-Time 不可能在 “best EMD package” 这个点上赢。

#### `PyWavelets`
wavelet 家族成熟、性能路径清楚，官方文档明确强调 high-level interface + low-level C/Cython performance；  
De-Time 只能把 wavelet 作为统一工作流中的一个入口，而不能把它写成方法深度优势。

#### `PySDKit`
这是最危险的对手。它已经公开定位为 signal decomposition library，并采用类似 scikit-learn 的统一接口；GitHub 体量和成熟度显著高于当前 De-Time。  
如果 De-Time 不能非常具体地证明自己的差异（统一结果模型、research workflow CLI、native kernels、time-series decomposition 结果契约、multivariate under same result object 等），reviewer 很容易认为你在一个**并不空白**的空间里做了“又一个整合包”。

#### `SSALib`
这是一个应当正面比较的 specialized competitor。它在 SSA 方向更专、更深，还有 JOSS 论文。  
De-Time 相对它的优势是 cross-family workflow；劣势是 SSA family depth 不如专门包。

### 1.7 一个额外但重要的命名现实

PyPI 上 `detime` 这个名字已经被另一个与 decimal time 相关的项目占用；你当前 distribution 名称是 `de-time`，而 import 是 `detime`。  
这本身不是错误，但会增加命名沟通成本。所以：

- 现在**不要**在投稿前再折腾 distribution rename；
- 但所有 docs、paper、website、CLI 帮助页都必须统一写清楚：  
  `pip install de-time`，`import detime`，`De-Time` 是软件品牌名。

---

## 2. 目标态：你要把 De-Time 改成什么样

投稿时 reviewer 应该看到的是下面这个对象，而不是当前混合态：

### 2.1 目标软件身份
- **品牌名**：De-Time
- **distribution**：`de-time`
- **canonical import**：`detime`
- **legacy alias**：`tsdecomp`（只作为过渡层，且带 deprecation warning；不再作为第一类公共身份）

### 2.2 目标 installable artifact
发布工件中应只包含：

- `src/detime/**`
- 必要的 native source
- tests
- examples
- 用户文档与开发文档
- license / citation / changelog / contributing / security

不应把以下内容作为核心 release 内容一起发出去：

- `src/synthetic_ts_bench/**`
- submission 文稿
- JMLR checklist / internal review files
- agent / manuscript / benchmark-specific orchestration code

### 2.3 目标 public surface
公开对用户讲的“主路径”只保留：

- Python：`decompose(series, config)`
- 结果对象：`DecompResult`
- 配置对象：`DecompositionConfig`
- CLI：`run`, `batch`, `profile`

Benchmark、leaderboard、artifact comparison 等只应当：
- 移到独立 benchmark repo / top-level `benchmarks/` 目录；
- 或作为 `detime-bench` / optional extra；
- 或完全不进入公开软件首页与主文档路径。

### 2.4 目标 JMLR 叙事
论文与网站都应该统一成同一个定位：

> De-Time 是一个面向可复用 time-series decomposition workflow 的研究软件层；  
> 它不是新算法，不试图替代每一个 specialized family library，核心贡献在于统一结果契约、统一 API/CLI、同一 public model 下的 multivariate support，以及对少数核心方法的原生加速与可分发工程化。

---

## 3. 修改总路线图（按优先级）

---

## 3A. P0：软件身份与包边界手术（必须先做）

### 3A.1 让 `detime` 变成真正的 canonical implementation
**当前问题**：`detime` 是 shim。  
**目标**：`detime` 成为主实现，`tsdecomp` 退化为兼容层。

#### 具体动作
1. 将 `src/tsdecomp` 中的真实实现迁移到 `src/detime`。
2. 修改内部 imports，使所有主实现都以 `detime.*` 为根。
3. 将 `src/tsdecomp` 改造成真正的 compatibility package：
   - 只做 re-export；
   - `import tsdecomp` 时发出 `DeprecationWarning`；
   - CLI alias 也发 warning。
4. 在 tests 中保留兼容性测试，但将其标注为 legacy-compat，而不是等价主路径。
5. 在 docs 和 README 中彻底消除 “`tsdecomp` 仍是一个并列主身份” 的印象。

#### 验收标准
- `src/detime` 中存在真实实现，而不是一层 re-export；
- `grep -R "from tsdecomp"` 在 `src/detime` 内不再出现；
- `tsdecomp` 只承担兼容别名，不再是 canonical public surface；
- paper 里可以理直气壮地写：`detime` is the canonical import, `tsdecomp` is a deprecated legacy alias.

### 3A.2 将 benchmark 工件从 installable package 中拆出去
**当前问题**：`src/synthetic_ts_bench` 还在 `src/` 里，sdist include 也显式打包。  
**目标**：软件 release 不再把 benchmark artifact 当核心软件的一部分分发。

#### 两种可选方案
**方案 A（更推荐）**：迁移到独立仓库  
- 新建 `de-time-bench` 或 `de-time-artifacts` 仓库。
- 主仓库只保留最小 bridge 文档与 reproducibility note。

**方案 B（可接受）**：留在同仓库，但搬出 installable `src/`
- 移到顶层 `benchmarks/`、`paper_artifacts/` 或 `research_artifacts/`
- 不进入 `pip install de-time` 的 wheel / sdist 主内容
- 文档中降级为 developer/research appendix，而非 public software surface

#### 同步要做的事
- 从 `pyproject.toml` 的 sdist include 中移除：
  - `src/synthetic_ts_bench/**/*.py`
  - `JMLR_*`
  - submission 相关文件
- 保留必要 examples，但 examples 必须是软件使用示例，而不是 benchmark orchestration。

#### 验收标准
- `pip install de-time` 的 wheel 安装后，不包含 benchmark package；
- 发布的 sdist 里不再出现 `synthetic_ts_bench` 与 JMLR submission 文件；
- reviewer 打开代码归档包时，看到的是软件，不是投稿工作区。

### 3A.3 剪掉 benchmark 气味过重的公开 CLI
**当前问题**：公开 API 文档还展示 `eval`, `validate`, `run_leaderboard`, `merge_results`。  
**目标**：主软件 CLI 只保留可被正当描述为“软件贡献”的部分。

#### 建议的公开 CLI
- `detime run`
- `detime batch`
- `detime profile`
- 可新增：
  - `detime methods`
  - `detime doctor`
  - `detime version`

#### 应降级 / 外移的命令
- `eval`
- `validate`
- `run_leaderboard`
- `merge_results`

这些命令要么：
- 移到 `detime-bench`；
- 要么改成 hidden/internal；
- 要么只保留在 benchmark repo 中。

#### 验收标准
- `detime --help` 展示的是干净、稳定的 user story；
- API 文档不再把 benchmark orchestration 命令当成主软件能力；
- paper 中不需要为这些命令辩护。

---

## 3B. P1：网站 / 文档重构（这是第二大审稿面）

### 3B.1 重建 docs 信息架构
当前 `mkdocs.yml` 顶层 nav 过于“平铺”，而且把不该前置的页面放到了主导航。  
建议改成：

1. Home
2. Why De-Time
3. Install
4. Quickstart
5. Choose a Method
6. Methods
7. API
8. Architecture
9. Tutorials
10. Comparisons
11. Migration from `tsdecomp`
12. Contributing
13. Citation / Releases

#### 应从主导航移出的页面
- `Visual Benchmark Heatmaps`
- `Agent Tools`
- `Project Files and Citation`（可拆分成 Citation + Developer Docs）
- 任何 manuscript / internal tooling / submission-facing 页面

### 3B.2 网站首页要只讲一个故事
首页现在的方向不算错，但还不够锋利。  
首页应严格回答 5 个问题：

1. **这是什么**：workflow-oriented research software for reproducible time-series decomposition
2. **不是什么**：not a new algorithm, not a benchmark paper, not a replacement for every specialized library
3. **最稳定的起点是什么**：`STD`, `STDR`, `SSA`, `MSSA`
4. **为什么值得用**：common result contract, one API, multivariate under same surface, selective native kernels
5. **怎么开始**：`pip install de-time`; `import detime`; 20 行 quickstart

### 3B.3 增加 reviewer 真正关心的文档页
必须新增或重写下面几页：

#### `why.md`
清楚写：
- 生态碎片化问题是什么；
- De-Time 的软件贡献边界是什么；
- 与上游 specialized libraries 的关系是什么。

#### `architecture.md`
给一个极简架构图：
- public API / CLI
- config + result contracts
- registry
- native-backed methods
- built-in methods
- wrapper methods
- optional multivariate backends
- serialization / profiling path

#### `comparisons.md`
这是给 reviewer 看的关键页面。  
必须包含一个真正有杀伤力的软件比较表，至少比较：

- `statsmodels`
- `PyEMD`
- `PyWavelets`
- `PySDKit`
- `SSALib`

比较维度建议：

- primary scope
- canonical result object
- unified cross-family interface
- multivariate under same top-level API
- batch CLI
- profiling workflow
- native kernels
- wrapper transparency / maturity labels
- install docs
- API docs
- CI / tests / coverage
- community evidence

#### `migration.md`
讲清楚：

- `pip install de-time`
- `import detime`
- `import tsdecomp` 还可用多久
- 哪些旧命令/旧路径被废弃
- 旧脚本怎么迁移

### 3B.4 文档中的 benchmark 页如何处理
建议不要完全删除 benchmark 页面，而是**降权与改位**：

- 放在 `Developer / Research Artifacts` 子区；
- 页面顶部写清楚：
  - 这不是主软件入口；
  - 这不是 JMLR software contribution 的核心；
  - 这些内容用于内部 comparison 或研究复现。

如果你继续把 benchmark heatmaps 放在顶层 nav，审稿人会认为你还没决定自己是软件还是 benchmark artifact。

### 3B.5 文档风格建议
当前站点使用最基础的 `mkdocs` 主题。  
这不是硬伤，但对软件审稿来说，建议升级为更稳的 docs 形态，例如：

- `mkdocs-material`
- 带 search、code tabs、admonitions
- 清楚的左侧层级导航
- 页面顶部放 stability / maturity / backend badges

这不是为了“好看”，而是为了强化“这是维护中的软件，不是 paper supplement”。

---

## 3C. P1：测试、CI、wheel、release 工程补硬

### 3C.1 coverage 要从“会生成报告”变成“有门槛”
当前 `.coveragerc` 只有 source / omit / report 配置，没有公开的 fail-under 门槛；CI 虽生成 coverage.xml / json / html，但没有看到 coverage threshold enforcement。

#### 建议动作
1. 给 `detime` 主包设定 `fail_under`：
   - 第一步可先设 90
   - 第二步拉到 95+
2. 对 legacy alias `tsdecomp` 单独处理：
   - 不要求与主包同等 coverage；
   - 但兼容层要有测试。
3. 在 README / docs 放 coverage badge。

#### 审稿收益
JMLR 明确说 coverage 应接近 100%。  
你未必真能到 100%，但至少要显示你**认真把 coverage 作为门槛，而不是仅仅生成一个报表**。

### 3C.2 wheel workflow 增加 smoke-test 安装验证
当前 `wheels.yml` 展示了多平台 wheel 构建和 PyPI publish，但没有清楚看到“下载 wheel 后在全新环境里安装并跑 smoke test”的环节。

#### 建议补充
每个平台构建完 wheel 后增加 job：

- 新环境安装 wheel
- `python -c "import detime; print(detime.__all__)"`
- `detime --help`
- 运行一个最小 univariate decomposition
- 在 Linux 上再跑一个最小 native-backed path 测试
- 若 `multivar` extra 存在，再跑一个 optional backend smoke test

### 3C.3 release artifact 自查
发布工件必须验证：

- `sdist` 能安装
- `wheel` 能安装
- `twine check` 通过
- 没有多余 submission / cache / macOS junk files
- release 说明与 CHANGELOG 一致
- wheel 安装后 `pip show de-time` 元数据与 docs 一致

### 3C.4 method maturity tests
既然文档中已经把方法分成 flagship / stable wrapper / experimental wrapper，测试结构也应跟着分层：

- `tests/core/`：`DecompResult`, `DecompositionConfig`, registry, serialization
- `tests/flagship/`：`STD`, `STDR`, `SSA`, `MSSA`
- `tests/wrappers/`：`STL`, `MSTL`, `EMD`, `WAVELET`
- `tests/legacy/`：`tsdecomp` alias
- `tests/cli/`：`run`, `batch`, `profile`
- `tests/bench_artifact/`：如果保留 benchmark tools，应单独分区，不进入核心 coverage 叙事

### 3C.5 reproducibility page
建议增加一页 `reproducibility.md`，明确写：

- Python version support
- OS support
- optional extras
- wheel-first install policy
- when source build is needed
- native extension fallback behavior
- known limitations

这页对 reviewer 非常有用，因为它直接回答“这软件到底能不能装、能不能复现”。

---

## 3D. P1：paper 与 cover letter 的重写路线

### 3D.1 标题、摘要、引言必须统一降维
正确的主线不是“很多方法都支持”，而是：

> fragmented ecosystem → reusable workflow layer → unified result/config contract → multivariate under same public model → selective native kernels → standalone package extracted from a larger artifact

摘要必须明确写出：
- **不是新算法**
- **不是要替代 specialized family packages**
- **贡献是 software architecture / unified workflow / engineering quality**

### 3D.2 Related software 不能只放 scope table
当前 draft 的 qualitative table 不够。  
建议改成两层表：

#### 表 1：生态定位图
比较：
- classical-depth
- family-specific-depth
- unified workflow layer
- multivariate support
- result contract

#### 表 2：软件增量表
比较维度：
- common result model
- one config object
- batch CLI
- profiling CLI
- multivariate under same top-level API
- native kernels
- maturity labels
- docs website
- CI
- coverage policy
- release artifacts

### 3D.3 必须补一个定量软件结果节
JMLR 明确点名 runtime / memory / features 比较。  
目前如果没有定量 evidence，很容易被说成“软件定位描述很多，但 progress 不够硬”。

#### 建议最少做的实验
1. `native` vs `python fallback`
   - `STD`
   - `STDR`
   - `SSA`
   - `DR_TS_REG`（若保留）
2. `flagship methods` 的规模曲线
   - 序列长度变化
   - 通道数变化（对 `MSSA` / channelwise path）
3. installation / support matrix
   - Linux / macOS / Windows
   - wheel available / source build fallback

#### 不建议做的事
- 不要做一大堆 scientific benchmark 结果表；
- 不要把软件 paper 写成 benchmark paper；
- 不要为了“有比较”去做不公平对比。

### 3D.4 必须单独加 “relationship to earlier artifact” 表
这一节不要只写历史说明，必须把 delta 做成**软件边界对照表**：

| Earlier artifact | Current package |
|---|---|
| benchmark orchestration mixed with reusable code | reusable package isolated |
| benchmark CLI commands exposed | compact public CLI |
| no clean canonical import | `detime` canonical |
| mixed package/research files in release | software-only release artifact |
| docs partly benchmark-facing | user-first docs and architecture pages |

这样 reviewer 才容易接受“这不是旧东西换皮”，而是边界清理后的独立软件对象。

### 3D.5 cover letter 的处理原则
你已经在 cover letter 里诚实承认：
- 不是新算法
- adoption 还早
- 来自 earlier benchmark artifact

这很好，但还不够。  
下一版 cover letter 应补强：

1. **active user community 证据**
   - 如果外部 adoption 仍早，不要编；
   - 但至少说明开放贡献机制、issue tracker、docs、release policy、maintainer structure；
   - 若有内部跨项目使用、下游实验室使用、课程或组内复用，只有在真实可披露时再写。
2. **software delta**
   - 明确列出相对 earlier artifact 的 substantive software improvements。
3. **comparison posture**
   - 正面承认 specialized upstream libraries；
   - 说明 De-Time 的差异是 workflow layer 与 result contract，而不是“比所有上游都强”。

---

## 3E. P2：社区与开放性证据的补强

JMLR MLOSS 对 active user community 是有明文要求的，而你当前 GitHub 公共数字非常弱。  
在不造假的前提下，能做的补强有：

### 3E.1 把“开放性”做实
- 开启 GitHub Discussions
- 增加 issue templates
- 增加 bug report / feature request templates
- 给 CONTRIBUTING 明确开发环境、测试、风格、release 流程
- 增加 developer architecture page
- 用 tagged release 和 release notes 展示维护节奏

### 3E.2 把 citation 与 archival 做实
- 保持 `CITATION.cff`
- 绑定 Zenodo DOI（如果尚未做）
- release 对应 archived source snapshot

### 3E.3 不要虚报 adoption
如果 stars / forks / watchers 仍低，就老实写“external adoption is still early”。  
但这时必须把其余项做得非常硬：
- docs
- CI
- tests
- release
- architecture clarity
- comparison evidence

---

## 4. 具体实施顺序（建议 6 个阶段）

## 阶段 1：身份与目录重构
**目标**：把最危险的 reviewer 质疑点先消掉。

- [ ] `detime` 变主实现
- [ ] `tsdecomp` 变 deprecated alias
- [ ] benchmark code 搬出 `src/`
- [ ] `pyproject.toml` 清理 sdist include
- [ ] 删除 release 中的 submission / agent / manuscript 文件
- [ ] CLI 只保留公开核心命令

**阶段结束判据**：  
一个外部 reviewer 下载源码时，第一眼看到的是软件，而不是 benchmark artifact。

## 阶段 2：网站 IA 重构
**目标**：让 docs 站能独立承担“软件身份说明”的任务。

- [ ] 重写首页
- [ ] 加 `why.md`
- [ ] 加 `architecture.md`
- [ ] 加 `comparisons.md`
- [ ] 加 `migration.md`
- [ ] benchmark 页移出主导航
- [ ] 明确 stable / wrapper / experimental 标识

**阶段结束判据**：  
一个 reviewer 不看 paper，只看 docs，也能理解软件贡献边界。

## 阶段 3：测试 / CI / release 加固
**目标**：把“工程化”从存在性证明升级成审稿级证据。

- [ ] coverage fail-under
- [ ] wheel smoke test
- [ ] sdist smoke install
- [ ] `twine check`
- [ ] README / docs badges
- [ ] 按方法成熟度分层测试

**阶段结束判据**：  
可以把 coverage、CI matrix、wheel installability 当成 paper 与 cover letter 中的硬证据来写。

## 阶段 4：软件比较与定量证据
**目标**：补齐 JMLR 最看重的“相对已有软件的推进”。

- [ ] competitor feature matrix
- [ ] native vs python runtime results
- [ ] installability/support matrix
- [ ] public docs comparison page
- [ ] paper 内简洁引用和表格

**阶段结束判据**：  
related software section 不再只是 qualitative positioning，而有真正的 software delta evidence。

## 阶段 5：paper 重写
**目标**：把叙事统一到 workflow-oriented software layer。

- [ ] 重写 title / abstract / intro
- [ ] 重写 related software
- [ ] 加 architecture figure / table
- [ ] 加 earlier-artifact delta table
- [ ] 删掉或降权 benchmark-heavy 表述
- [ ] 核对所有 claims 与 repo 现状一致

**阶段结束判据**：  
paper 与仓库、网站、cover letter 三者完全一致，不互相打脸。

## 阶段 6：最终 submission bundle
**目标**：把最后一轮最容易漏掉的点卡死。

- [ ] version tag 固定
- [ ] code archive 自查
- [ ] docs deploy 对应 reviewed version
- [ ] cover letter 最终核对
- [ ] JMLR checklist 最终核对
- [ ] reviewer 自测（像陌生 reviewer 一样从头装一次）

---

## 5. 建议的仓库改造后结构

```text
De-Time/
├─ src/
│  ├─ detime/                  # canonical package
│  └─ tsdecomp/                # deprecated alias only
├─ native/
├─ tests/
├─ examples/
├─ docs/
├─ benchmarks/                 # optional, not installable
├─ submission/                 # optional, not in release artifact
├─ README.md
├─ pyproject.toml
├─ mkdocs.yml
├─ CHANGELOG.md
├─ CITATION.cff
├─ CONTRIBUTING.md
├─ SECURITY.md
└─ ROADMAP.md
```

如果条件允许，更好的方案是：

```text
de-time/           # software repo
de-time-bench/     # benchmark / artifact repo
```

---

## 6. 你在稿子里最该坚持的几句“边界句”

这些话应该在网站、README、paper、cover letter 里保持一致：

1. **De-Time is not a new decomposition algorithm.**
2. **De-Time is a workflow-oriented research software layer for reproducible time-series decomposition.**
3. **The canonical public package is `detime`; `tsdecomp` is a deprecated compatibility alias.**
4. **The package does not attempt to replace specialized family-specific libraries such as `statsmodels`, `PyEMD`, `PyWavelets`, `PySDKit`, or `SSALib`.**
5. **Its main contribution is a unified result/config contract, one public API and CLI, multivariate support under the same software surface, and selective native acceleration for selected high-cost methods.**
6. **Benchmark artifacts and research-orchestration code are kept distinct from the installable software release.**

---

## 7. 风险与对应策略

### 风险 1：大规模 namespace 重构会破坏兼容性
**策略**：先在一版 release 中保留 `tsdecomp` warning alias；同时提供 migration guide 和 alias tests。

### 风险 2：拆 benchmark code 会让部分现有脚本失效
**策略**：把 benchmark 迁到独立 `benchmarks/` 或 companion repo，并留兼容桥接脚本。

### 风险 3：active user community 证据仍然偏弱
**策略**：不要造假；把 openness、release hygiene、docs、tests、CI 做到极硬；在 cover letter 里如实承认 adoption early。

### 风险 4：native wheel support 可能在平台上不稳
**策略**：加 smoke install，明确 wheel-first / source-fallback 策略；paper 不要过度承诺“全平台无痛原生加速”。

### 风险 5：related software 对比做得不公平
**策略**：只比较软件层面的可验证维度；运行时间比较只做同方法、同任务、同配置下的公平 comparison；不做“跨家族谁更准”这种 scientific benchmark。

---

## 8. Definition of Done（投稿前必须同时满足）

### 软件层面
- [ ] `detime` 不是 shim，而是主实现
- [ ] `tsdecomp` 只是 deprecated compatibility alias
- [ ] release artifact 中不含 benchmark package 与 submission 文件
- [ ] CLI 公开表面收缩到 `run / batch / profile` 等稳定路径
- [ ] docs 站主导航不再前置 benchmark / agent / manuscript 内容

### 工程层面
- [ ] coverage 有 fail-under
- [ ] wheel 和 sdist 都有 smoke install
- [ ] CI 覆盖 Linux/macOS/Windows 与多 Python 版本
- [ ] docs build 严格模式通过
- [ ] versioned release 与 reviewed source archive 一致

### 论文层面
- [ ] abstract / intro / README / docs 首页叙事一致
- [ ] related software 有 feature/runtime/support 对比
- [ ] 与 earlier artifact 的 delta 明确且 substantive
- [ ] 所有 claims 都能在代码、docs、CI 或实验表中找到依据
- [ ] 没有把 benchmark 结果包装成软件贡献

---

## 9. 最后判断

如果你只改 paper，不改仓库边界，**大概率仍会被严厉 reviewer 打回**。  
如果你完成上面的 P0 + P1，并至少补出一个可信的软件比较节，那么它就会从：

> “整理过的 benchmark artifact / renamed wrapper”

转成：

> “边界清楚、可复用、可审的软件研究对象”

这才是 JMLR MLOSS 会认真审的软件形态。

---

## 10. 证据索引（供写作与开发时交叉核对）

- **[E1]** JMLR MLOSS 审稿要求：active user community、runtime/memory/features 比较、tutorials、API docs、coverage 接近 100%、CI。
- **[E2]** JMLR 作者说明：claims 必须有证据；与既有/并行工作要有 substantive delta。
- **[E3]** `submission/cover_letter_jmlr_mloss.md`：软件来自 earlier benchmark artifact；adoption 仍早期；不是新算法。
- **[E4]** `submission/jmlr_mloss_software_paper_draft.md`：workflow-oriented 软件定位；但仍保留 dual identity。
- **[E5]** `README.md`：当前 public brand / distribution / import 的表述。
- **[E6]** `pyproject.toml`：双 CLI entrypoint、sdist include 仍包含 benchmark 与 submission 文件。
- **[E7]** `src/detime/__init__.py`：`detime` 是 thin compatibility-first shim。
- **[E8]** `src/detime/cli.py`：CLI 只是转发到 `tsdecomp.cli`.
- **[E9]** `tests/test_branding_imports.py`：显式测试 `detime` 与 `tsdecomp` 双路径。
- **[E10]** `docs/api.md`：CLI 公开暴露 `eval`, `validate`, `run_leaderboard`, `merge_results`。
- **[E11]** `mkdocs.yml`：主导航包含 `Visual Benchmark Heatmaps`、`Agent Tools` 等。
- **[E12]** `docs/tutorials/visual-benchmark.md`：公开 benchmark heatmap 风格页面，并承认 full benchmark stack 更 research-artifact flavored。
- **[E13]** `docs/methods.md`：清楚列出 flagship / stable wrapper / experimental wrapper。
- **[E14]** `src/tsdecomp/core.py`：`DecompResult` / `DecompositionConfig` 的统一结果和配置契约。
- **[E15]** `src/tsdecomp/registry.py`：统一 `decompose(...)` 入口与 input mode 处理。
- **[E16]** `.github/workflows/ci.yml`：Linux/macOS/Windows + 多 Python 版本测试、coverage、docs build。
- **[E17]** `.github/workflows/wheels.yml`：多平台 wheel 构建与 publish，但需补 smoke-test install。
- **[E18]** `.coveragerc`：当前未见 fail-under 门槛。
- **[E19]** GitHub 仓库首页：当前 stars / forks / commits 很低，社区证据弱。
- **[E20]** PySDKit：统一 signal decomposition 库，社区规模与仓库成熟度更强。
- **[E21]** PyEMD：EMD family 深度与社区规模明显更强。
- **[E22]** PyWavelets：成熟 wavelet 库，强调 high-level API + low-level C/Cython performance。
- **[E23]** SSALib：SSA 专门库，已有 JOSS 论文，专门深度更强。
- **[E24]** statsmodels MSTL/STL：classical decomposition 方向成熟。
- **[E25]** PyPI `detime` 名称已被他用；当前 `de-time` distribution / `detime` import 的文档必须写清。
