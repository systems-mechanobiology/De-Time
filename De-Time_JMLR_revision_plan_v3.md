# De-Time JMLR MLOSS 重审与修改开发计划（v3）

> 审查基准：2026-04-07 对公开 GitHub 仓库、公开文档源码、公开工作流/打包配置、JMLR MLOSS 审稿标准、以及同类软件公开页面的核查结果。  
> 审稿角色设定：**JMLR software track reviewer，偏严格/挑剔版本**。  
> 当前总体判断：**仍然偏 weak reject / major revision；不建议现在提交。**

---

## 0. 一句话结论

你这轮修改把 **README / docs / CI / wheels / branding / Methods Atlas / submission draft** 都补得更像“一个软件包”了；但 **JMLR MLOSS 真正最看重的几件事仍没有压实**：

1. **软件身份还没有真正独立**：`detime` 公开层现在仍然是 `tsdecomp` 的 compatibility-first shim，而不是 canonical implementation。  
2. **公共网页和 installable package 仍在泄漏 benchmark artifact 身份**：docs 导航、API 页面、examples、sdist 内容都还暴露 leaderboard / benchmark / agent / synthetic bench。  
3. **与同类软件的“显著进步”还没有被证明**：尤其是对 `PySDKit` 和 `SSALib` 的正面对比仍不够。  
4. **社区采用与 release 证据仍然太弱**：0 stars / 0 forks / 0 issues / 0 PRs / 无 GitHub release / 仅 11 commits。  
5. **MLOSS 适配叙事仍偏弱**：你需要更明确回答“这为什么是给 machine learning 社区的软件，而不是更适合 JOSS 的科学计算/信号处理工具”。

---

## 1. 如果我是很 mean 的 reviewer，我会怎么写

### Overall recommendation
**Weak Reject / Reject, invite resubmission after substantial package-boundary cleanup and stronger evidence of independent software contribution.**

### Why
The repository is visibly closer to reviewable software than a raw benchmark artifact, but the public package identity is still not clean. The `detime` namespace remains a thin re-export layer over `tsdecomp`; the public documentation still surfaces benchmark-style and agent-facing pages; the source distribution still bundles synthetic benchmark code and reviewer-facing files; and the related-software argument still understates the most relevant adjacent packages (`PySDKit`, `SSALib`) while relying on an outdated framing around `vmdpy`. In its current form, the project reads more like a carefully packaged extraction from a research artifact than a fully stabilized standalone software contribution.

### What would change my mind
I would want to see:
- `detime` become the actual implementation namespace, with `tsdecomp` demoted to a thin alias package or removed from the reviewed artifact.
- the public docs and installable source package cleaned of benchmark-only, leaderboard, synthetic-benchmark, and agent-facing material;
- a stronger, more current related-software comparison centered on `PySDKit`, `SSALib`, `PyEMD`, `PyWavelets`, `statsmodels`, and the `sktime`-hosted `vmdpy` story;
- explicit release evidence, quantitative software-quality evidence, and a sharper explanation of the package’s relevance to the machine learning community.

---

## 2. 按 JMLR MLOSS 标准逐条深度诊断

JMLR MLOSS 明确会看：  
- active user community  
- 与既有实现相比的 runtime / memory / features  
- 安装文档、tutorial、API 文档  
- 开发者开放性与软件设计清晰度  
- 大量单元/集成测试，且 coverage **接近 100%**  
- 多平台 CI 与可用性  
来源：JMLR MLOSS 官方标准。  
参考：[JMLR MLOSS](https://www.jmlr.org/mloss/mloss-info.html)

### 2.1 你这轮修改做对了什么

#### A. public docs 结构明显比之前像“真软件”
README、Install、Quickstart、API、Methods Atlas、Project Status、Examples 这些入口都在，且 `mkdocs.yml` 确实把它们组织成独立网站结构。  
这对 MLOSS 是加分项，因为 reviewer 会明确检查 installation / tutorials / API docs / website 可访问性。  
参考：`README.md`、`docs/*.md`、`mkdocs.yml`；以及 JMLR MLOSS user documentation criteria。  
- [README](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/README.md)  
- [mkdocs.yml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/mkdocs.yml)  
- [JMLR MLOSS](https://www.jmlr.org/mloss/mloss-info.html)

#### B. Methods Atlas 把“backend story / maturity boundary”写出来了
这点是对的。你没有把所有方法都包装成“同等成熟的自研实现”，而是区分了：
- native-backed flagship (`SSA`, `STD`, `STDR`, `DR_TS_REG`)
- built-in (`MSSA`)
- wrappers / optional backends (`EMD`, `CEEMDAN`, `VMD`, `MVMD`, `MEMD`, `WAVELET`, etc.)
这比很多软件论文更诚实。  
参考：[Methods Atlas](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/methods.md)

#### C. CI / wheels / docs workflow 已经具备 reviewer 可见的工程骨架
你现在确实有：
- multi-OS CI
- coverage job
- docs build
- cibuildwheel build + wheel smoke tests
这说明你知道 software track 会审工程质量，而不是只看算法。  
参考：  
- [CI](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.github/workflows/ci.yml)  
- [wheels](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.github/workflows/wheels.yml)  
- [docs workflow](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.github/workflows/docs.yml)  
- [cibuildwheel.toml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/cibuildwheel.toml)

#### D. 有真实的 native extension story，不是空喊“高性能”
`_native.py` 明确做了 optional native extension import、capabilities 检查和 fallback。这说明 native story 是真的。  
参考：[src/tsdecomp/_native.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/tsdecomp/_native.py)

---

## 3. 目前最致命的问题

### 3.1 `detime` 还不是软件的真实主体，而是 `tsdecomp` 的公共外壳

这是当前最伤的一点。

公开源码直接写明：
- `src/detime/__init__.py`：`detime` 是 a **thin compatibility-first shim over the legacy tsdecomp implementation**
- `src/detime/core.py` / `registry.py` / `cli.py` / `backends.py` / `io.py` / `profile.py` 仍是对 `tsdecomp` 的 re-export 或 shim
- `PUBLISHING.md` 还明确写着当前仓库“**keeps the implementation under `src/tsdecomp/` and adds `src/detime/` as a compatibility-first public shim**”

这意味着 reviewer 很容易写出一句非常伤的话：

> The rebranding is visible, but the reviewed software identity is still transitional rather than stabilized.

参考：  
- [src/detime/__init__.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/__init__.py)  
- [src/detime/core.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/core.py)  
- [src/detime/registry.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/registry.py)  
- [src/detime/cli.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/cli.py)  
- [PUBLISHING.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/PUBLISHING.md)

**这不是 cosmetic 问题，而是 software contribution boundary 问题。**

如果 reviewer 问：“你投稿的软件到底叫什么？真正实现在哪？reviewed artifact 是 `detime` 还是 `tsdecomp`？legacy alias 会保留多久？为什么不直接 canonicalize？”  
你现在的公开状态还不能给出一个干净答案。

---

### 3.2 公共 docs 和 installable package 仍在泄漏 benchmark artifact 身份

你 README 里已经写了 “not a benchmark artifact pretending to be a library”，但当前公共表面并没有完全做到这一点。

#### 证据一：docs 导航仍包含 benchmark / agent 页面
`mkdocs.yml` 公开导航还包含：
- `Visual Benchmark Heatmaps`
- `Agent Tools`

参考：[mkdocs.yml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/mkdocs.yml)

#### 证据二：公开 API 仍把 leaderboard 命令列为 exposed CLI
`docs/api.md` 里公开列了：
- `eval`
- `validate`
- `run_leaderboard`
- `merge_results`

虽然页面里又说 “first-class user path today is `run`, `batch`, `profile`”，但 reviewer 不会帮你做善意解释；他会直接说你 public surface 仍混有 benchmark orchestration。  
参考：[docs/api.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/api.md)

#### 证据三：公开 tutorial 仍有 “visual leaderboard heatmaps”
`docs/tutorials/visual-benchmark.md` 明确写的是 leaderboard-style heatmaps，还使用 synthetic scenarios 和 benchmark-style summary metrics。  
这会持续削弱“standalone software library”叙事。  
参考：[visual-benchmark.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/tutorials/visual-benchmark.md)

#### 证据四：Example Gallery 仍突出 benchmark heatmap walkthrough
`docs/examples.md` 仍把 `visual_leaderboard_walkthrough.py` 作为 gallery 核心页面之一。  
参考：[examples.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/examples.md)

#### 证据五：sdist 仍打包 `synthetic_ts_bench` 与 reviewer-facing 材料
`pyproject.toml` 的 sdist include 仍包含：
- `src/synthetic_ts_bench/**/*.py`
- `JMLR_SOFTWARE_IMPROVEMENTS.md`
- `JMLR_MLOSS_CHECKLIST.md`
- `AGENT_MANIFEST*`
- `AGENT_INPUT_CONTRACT.md`

`MANIFEST.in` 也继续 include JMLR reviewer-facing files。  
这会让 reviewer 说：**你嘴上说这是 standalone software，包里却还在打包 benchmark-support code 和 submission-facing clutter。**  
参考：  
- [pyproject.toml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/pyproject.toml)  
- [MANIFEST.in](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/MANIFEST.in)

---

### 3.3 release story 仍不完整，外部采用证据仍然几乎为零

当前公开 GitHub 仓库显示：
- 0 stars
- 0 forks
- 0 issues
- 0 pull requests
- 11 commits
- no releases
- no tags

参考：  
- [repo main page](https://github.com/systems-mechanobiology/De-Time)  
- [releases](https://github.com/systems-mechanobiology/De-Time/releases)  
- [tags](https://github.com/systems-mechanobiology/De-Time/tags)

而你的 cover letter 也明确承认：
> external public adoption is still early  
参考：[cover letter](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/submission/cover_letter_jmlr_mloss.md)

JMLR MLOSS 官方标准明确要求 cover letter 里提供 active user community evidence。  
在当前状态下，reviewer 很容易给出结论：**软件可能有价值，但 community/adoption evidence 远不足以支撑“impact on the machine learning community”的高分。**  
参考：[JMLR MLOSS](https://www.jmlr.org/mloss/mloss-info.html)

---

### 3.4 related software 仍然没有打到最危险的对手

当前 `docs/research-positioning.md` 和 paper draft 主要围绕：
- `statsmodels`
- `PyWavelets`
- `PyEMD`
- `vmdpy`
- `PySDKit`

但问题是：

#### A. `PySDKit` 不是可有可无的对手，而是当前最危险的主对手
官方 GitHub 和 PyPI 公开写得非常清楚，`PySDKit` 的定位就是：
- signal decomposition in Python
- unified interface similar to scikit-learn
- 覆盖 univariate / multivariate / image decomposition
- public package + PyPI release + docs/examples
- 200 stars, 26 forks, 251 commits
- PyPI 最新版 0.4.23

而你的 `multivar` optional extra 还直接依赖 `PySDKit>=0.4.23`。  
这会让 reviewer 直接问：

> If your multivariate story relies on PySDKit, what is the independent software delta beyond a workflow wrapper?

参考：  
- [PySDKit GitHub](https://github.com/wwhenxuan/PySDKit)  
- [PySDKit PyPI](https://pypi.org/project/PySDKit/)  
- [你的 pyproject.toml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/pyproject.toml)

#### B. `SSALib` 应该被正面纳入 related software 核心表
你现在 strongest current methods 里把 `SSA` 放得很高，但 `SSALib` 已经是：
- 专做 SSA 的包
- 14 stars / 244 commits
- README 公开写 coverage 97%
- 多 SVD solvers
- Monte Carlo SSA
- built-in visualization
- JOSS 2025 已发表软件论文

如果你不把 `SSALib` 纳入核心对比，reviewer 会觉得你在规避“单方法深度型强对手”。  
参考：  
- [SSALib GitHub](https://github.com/ADSCIAN/ssalib)  
- [SSALib README](https://raw.githubusercontent.com/ADSCIAN/ssalib/main/README.md)  
- [JOSS paper](https://joss.theoj.org/papers/10.21105/joss.08600)

#### C. `vmdpy` 作为 active upstream 的写法已经过时
`vmdpy` 官方 README 明确说：
- 自 2023 年 8 月起由 `sktime` 分发和维护
- 安装路径是 `pip install sktime`
- vmdpy 仓库已 archive（2024-06-14）

所以如果你还把 `vmdpy` 写成活跃独立 competitor，会显得调研不新。  
正确写法应该是：**VMD path in De-Time should be compared against the `sktime`-hosted `vmdpy` lineage / implementation story**, not only the archived repository.  
参考：  
- [vmdpy GitHub](https://github.com/vrcarva/vmdpy)  
- [vmdpy README](https://raw.githubusercontent.com/vrcarva/vmdpy/master/README.md)  
- [sktime GitHub](https://github.com/sktime/sktime)

---

### 3.5 工程 best-practice 还没有达到“让 reviewer 不好下嘴”的程度

#### A. coverage story 不够硬
`.coveragerc` 只表明：
- source = detime tsdecomp
- omit = `*/tsdecomp/leaderboard.py`

但没有看到：
- fail-under threshold
- public coverage badge / exact coverage number
- PR gate based on coverage

MLOSS 标准明确说 reviewer 会看 testing 与 code coverage，且“expected to be close to 100%”。  
参考：  
- [JMLR MLOSS](https://www.jmlr.org/mloss/mloss-info.html)  
- [.coveragerc](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.coveragerc)  
- [CI](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.github/workflows/ci.yml)

#### B. 你一边公开展示 leaderboard，一边把 leaderboard.py 从 coverage 排除
这会引来非常不舒服的 reviewer comment：

> Why is publicly surfaced functionality omitted from coverage?

如果 `leaderboard` 是公开功能，就不该被 coverage 特判；  
如果它不是公开功能，就不该继续出现在 docs nav / API / example gallery。

#### C. release engineering 说得比做得多
你已经有 release workflow，但 GitHub 仓库当前还没有 public release/tag。  
`PUBLISHING.md` 甚至还写着 “Before the first public release confirm ... PyPI project name availability for `de-time`”。  
这说明 release contract **还没冻结**。  
参考：  
- [PUBLISHING.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/PUBLISHING.md)  
- [releases](https://github.com/systems-mechanobiology/De-Time/releases)

---

### 3.6 MLOSS 适配性还需要更强的“machine learning relevance”叙事

JMLR MLOSS 不是 JOSS。  
它要的是对 **machine learning community** 有意义的软件。JMLR 官方表述是“non-trivial machine learning algorithms, toolboxes or even languages for scientific computing”。  
De-Time 可以勉强落在 “scientific computing toolbox relevant to ML workflows” 这个框里，但现在公开 docs/README/paper 还没有把这件事讲得足够清楚。

当前 README/quickstart/tutorials 更像：
- decomposition research software
- signal / seasonal / multivariate workflows
而不是：
- ML preprocessing / feature extraction / model pipeline integration

这会给 mean reviewer 一个额外攻击点：

> The software may be useful, but the manuscript does not yet make a strong case for why JMLR MLOSS is the natural venue rather than a general scientific-software venue.

参考：  
- [JMLR MLOSS](https://www.jmlr.org/mloss/mloss-info.html)  
- [README](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/README.md)

---

## 4. 与同类相关工作的优缺点对比（站在 reviewer 视角）

### 4.1 对 `statsmodels`
**它的强项**
- `STL` / `MSTL` 是成熟、稳定、社区极强的 classical decomposition baseline
- 官方文档齐全
- 社区体量远大于 De-Time（GitHub 11.3k stars）
- `STL` / `MSTL` 都是正式 API，`MSTL` 也已在 0.14.0 加入

参考：  
- [statsmodels repo](https://github.com/statsmodels/statsmodels)  
- [STL docs](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html)  
- [MSTL docs](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.MSTL.html)

**De-Time 的优势**
- 提供 cross-family workflow，不止 classical
- 有统一 `DecompositionConfig` / `DecompResult`
- 有 CLI / batch / profile
- 可以把 classical + subspace + adaptive methods 放进同一运行面

**De-Time 的劣势**
- classical decomposition 深度远不如 `statsmodels`
- 没有证据表明 classical path 更快、更稳、更易用
- reviewer 不会接受“我们也支持 STL/MSTL，所以能和 statsmodels 正面对打”的写法

**结论**
你对 `statsmodels` 的正确姿态不是“替代它”，而是“把它并入统一 workflow layer”。

---

### 4.2 对 `PyEMD`
**它的强项**
- 专注 EMD family
- 有 `EMD`, `EEMD`, `CEEMDAN`, `JitEMD`, experimental 2D/BEMD
- 公开文档与 examples 齐全
- GitHub 974 stars / 230 forks / 228 commits
- 近年仍在更新（README 提到 2025-11 v1.9 / v1.8 changes）

参考：  
- [PyEMD repo](https://github.com/laszukdawid/PyEMD)  
- [PyEMD README](https://raw.githubusercontent.com/laszukdawid/PyEMD/master/README.md)

**De-Time 的优势**
- 可以把 EMD family 和非 EMD family 放到同一 contract 下
- 可以纳入 CLI / batch / profile workflow
- result contract 对 cross-method comparison 更友好

**De-Time 的劣势**
- 在 EMD family 深度上肯定输
- reviewer 会默认你这里是 wrapper path，不会把它看作 EMD 软件创新

**结论**
在 paper 和 docs 里不要暗示自己是更好的 EMD 软件；要写成 “EMD family is available inside the common decomposition workflow”.

---

### 4.3 对 `PyWavelets`
**它的强项**
- 极成熟的 wavelet library
- 1D / 2D / nD transforms
- 100+ built-in wavelet filters
- binary wheels, low dependency surface, source build story 清晰
- 2.4k GitHub stars，历史很长，JOSS citation 完整

参考：  
- [PyWavelets repo](https://github.com/PyWavelets/pywt)  
- [PyWavelets README](https://raw.githubusercontent.com/PyWavelets/pywt/main/README.rst)  
- [PyWavelets docs](https://pywavelets.readthedocs.io/en/latest/)

**De-Time 的优势**
- 能把 wavelet route 装进 decomposition-style output contract
- 适合把 wavelet 作为一个统一 baseline 参与 workflow

**De-Time 的劣势**
- wavelet 绝不是你的主战场
- reviewer 会把 `WAVELET` 看成 wrapper，不会看成你对 wavelet software 的贡献

**结论**
你的正确叙事是 “wavelet-based path inside a unified decomposition workflow”，不是 “wavelet capability comparable to PyWavelets”。

---

### 4.4 对 `PySDKit`（最危险）
**它的强项**
- 官方自我定位就是 unified signal decomposition library
- scikit-learn-like unified interface (`fit_transform`)
- PyPI 已发版（0.4.23）
- 覆盖 univariate / multivariate / image decomposition
- 200 stars / 26 forks / 251 commits
- 文档、示例、算法覆盖面都在快速扩展

参考：  
- [PySDKit GitHub](https://github.com/wwhenxuan/PySDKit)  
- [PySDKit PyPI](https://pypi.org/project/PySDKit/)

**De-Time 的可能优势**
- 更明确的 `trend / season / residual / components / meta` decomposition contract
- 更强调 research workflow（CLI / batch / profiling）
- 对 selected methods 有 native kernels
- Methods Atlas 对 maturity boundary 更诚实

**De-Time 的重大弱点**
- 你的 `multivar` extra 直接依赖 `PySDKit>=0.4.23`
- 这让 reviewer 很容易觉得：你的 multivariate breadth 很大程度是站在 `PySDKit` 上
- 若没有非常明确的 “De-Time delta” 证据，就会被看成 wrapper/orchestration layer

**结论**
你必须把对 `PySDKit` 的差异写成非常具体的 software delta，而不是抽象定位。  
建议你明确列出：

1. 统一 decomposition result contract（不仅是统一 fit_transform）
2. batch / profiling / serialization 工作流
3. native kernels 覆盖的核心方法
4. public docs 对 method maturity 的显式声明
5. 面向 reproducible decomposition experiments 的输出格式

否则 reviewer 很容易给一句：
> PySDKit already occupies the “unified decomposition library” niche more directly.

---

### 4.5 对 `SSALib`
**它的强项**
- 专门做 SSA
- 支持多个 SVD solver
- 有 Monte Carlo SSA
- 有 datasets 和 built-in plots
- README 公开 coverage 97%
- JOSS 2025 软件论文已发表
- 244 commits，软件成熟度比表面印象更强

参考：  
- [SSALib GitHub](https://github.com/ADSCIAN/ssalib)  
- [SSALib README](https://raw.githubusercontent.com/ADSCIAN/ssalib/main/README.md)  
- [JOSS paper](https://joss.theoj.org/papers/10.21105/joss.08600)

**De-Time 的优势**
- 跨 family workflow
- 同一 API 下还能去做 `STD`, `STDR`, `MSSA`, wrappers
- 更偏 workflow layer

**De-Time 的劣势**
- 一旦 reviewer按 `SSA` 深度打分，De-Time 很可能输
- 如果你把 `SSA` 写成 package strongest method，就必须解释为什么不是直接用 `SSALib`

**结论**
在 paper 的 related software 里，`SSALib` 必须出现，而且要正面承认它在 SSA family 上更深。

---

### 4.6 对 `vmdpy` / `sktime`
**事实**
- `vmdpy` 仓库已经 archive
- 官方 README 说从 2023 年 8 月起由 `sktime` 维护和分发
- `sktime` 本身是 9.7k stars / 2.1k forks 的大社区项目

参考：  
- [vmdpy repo](https://github.com/vrcarva/vmdpy)  
- [vmdpy README](https://raw.githubusercontent.com/vrcarva/vmdpy/master/README.md)  
- [sktime repo](https://github.com/sktime/sktime)

**含义**
你如果还把 `vmdpy` 写成一个独立活跃 competitor，会显得调研 outdated。  
related work 里至少要改成：
- VMD lineage / implementation path is currently maintained through `sktime`
- De-Time exposes VMD within a decomposition workflow contract rather than claiming a deeper VMD implementation

---

## 5. 最优修改路线：按优先级拆成 6 个 wave

---

## Wave 1（最高优先级）：先把软件身份定死

### 目标
让 reviewer 不再能说：**“`detime` 只是 `tsdecomp` 换壳。”**

### 必做动作
1. **把 `src/detime/` 变成真实实现主体**
   - 目标状态：`detime` 是 canonical implementation namespace
   - `tsdecomp` 只保留最薄 alias，或者干脆拆成单独 compatibility package
2. **删除 `src/detime/*` 中对 `tsdecomp` 的 re-export 依赖**
   - `__init__.py`, `core.py`, `registry.py`, `cli.py`, `backends.py`, `io.py`, `profile.py` 都应本地实现或本地 import
3. **把 legacy narrative 改成 one-way compatibility**
   - 文档里不再反复宣传 `tsdecomp`
   - 只在 migration / compatibility 页写明
4. **更新 `PUBLISHING.md`**
   - 不再写 “current repository keeps the implementation under `src/tsdecomp/`”
   - release contract 要以 `detime` 为唯一主体

### 为什么这是第一优先级
因为这决定 reviewer 到底把你看成：
- **独立软件**
还是
- **过渡中的 rebrand wrapper**

### 涉及文件
- `src/detime/*.py`
- `src/tsdecomp/*.py`
- `README.md`
- `docs/quickstart.md`
- `docs/install.md`
- `docs/api.md`
- `docs/project-status.md`
- `PUBLISHING.md`
- `ENTRYPOINTS.md`
- tests 中所有 `tsdecomp` 兼容性用例

### 完成标准
- `src/detime/` 中不再出现 `from tsdecomp ...`，除非在单独的 compatibility shim 包里
- public docs 首页与 quickstart 只展示 `detime`
- `tsdecomp` 不再被当作 equally first-class path
- `JMLR_MLOSS_CHECKLIST.md` 不再出现 “for `tsdecomp`”

---

## Wave 2：清理 public docs / website，让它看起来像库，而不是 artifact portal

### 目标
把 reviewer 的第一印象从“带 benchmark 残留的研究仓库”改成“边界清楚的 research software website”。

### 必做动作

#### 2.1 从主导航移除 benchmark / agent 页面
从 `mkdocs.yml` 主导航移除：
- `Visual Benchmark Heatmaps`
- `Agent Tools`

建议做法：
- 移到 `internal/` 或 `maintainer/` docs
- 或从公开站点完全去掉，只保留在仓库内部说明

#### 2.2 API 页面只保留真正 public 的命令
`docs/api.md` 应只列：
- `run`
- `batch`
- `profile`

把下面这些移出 public API 页：
- `eval`
- `validate`
- `run_leaderboard`
- `merge_results`

#### 2.3 删除或降级 leaderboard tutorial
`visual-benchmark.md` 与 `visual_leaderboard_walkthrough.py` 至少要做其一：
- 从 public docs 中删除
- 或改名为 `evaluation-internal.md`
- 或移入 separate benchmark artifact repo

#### 2.4 删除公开“Agent Tools”页面
这类页面会让 reviewer 觉得仓库目标混乱。  
`AGENT_*` 文件如果是内部工作流需要，可以保留在 repo，但不要作为 public docs 主导航的一部分。

#### 2.5 增加一个真正面向 MLOSS 的页面
新增：
- `docs/ml-workflows.md` 或 `docs/why-ml.md`

内容应解释：
- decomposition 如何作为 ML preprocessing / representation / feature extraction / interpretability support
- 为什么该软件对 machine learning community 有意义

### 涉及文件
- `mkdocs.yml`
- `docs/api.md`
- `docs/examples.md`
- `docs/tutorials/visual-benchmark.md`
- `docs/agent-friendly.md`
- `README.md`
- `docs/index.md`
- 新增 `docs/ml-workflows.md`

### 完成标准
- 导航首页不再出现 benchmark / leaderboard / agent 字样
- API 文档不再泄漏 benchmark 命令
- examples gallery 不再以 leaderboard heatmap 为 showcase
- 站点首页的第一印象是 library / workflows，而不是 artifact / agent / internal tooling

---

## Wave 3：清理 installable package 和 source distribution

### 目标
让 reviewer 能放心地说：**source package is clean**。

### 必做动作

#### 3.1 从 sdist 中移除 `src/synthetic_ts_bench`
这是当前最明确的 package-boundary 泄漏之一。  
如果 benchmark utilities 真的还要保留：
- 移到单独 repo
- 或移到 `contrib/benchmark_artifact/` 且不进入 release artifact

#### 3.2 从 sdist 中移除 reviewer-facing / maintainer-facing clutter
不要把这些打进 installable source package：
- `JMLR_SOFTWARE_IMPROVEMENTS.md`
- `JMLR_MLOSS_CHECKLIST.md`
- `JMLR_SUBMISSION_CHECKLIST.md`
- `AGENT_MANIFEST*`
- `AGENT_INPUT_CONTRACT.md`
- 其他 submission-only 文件

#### 3.3 清理 `MANIFEST.in`
`MANIFEST.in` 与 `tool.scikit-build.sdist.include` 要一致，且只包含：
- 软件必需源码
- docs/examples（若你坚持）
- license / citation / changelog / contributing
不要 include review materials.

#### 3.4 release artifact 中不要再出现 benchmark / submission 气味
最终 reviewer 下载的 code archive 应看起来像：
- 一个 package
- 一个 docs tree
- 一个 tests tree
而不是 mixed research folder

### 涉及文件
- `pyproject.toml`
- `MANIFEST.in`
- repo 目录结构
- 可能需要移动 `src/synthetic_ts_bench/`
- submission materials 位置整理

### 完成标准
- `python -m build --sdist` 后展开归档，里面没有 `synthetic_ts_bench`
- 归档里没有 `JMLR_*` 和 `AGENT_*`
- README 与 docs 不再解释这些 internal/review files 给普通用户

---

## Wave 4：把工程质量证据做成 reviewer 没法轻易挑刺的形式

### 目标
把 “有测试/有 CI” 提升成 “有可量化的质量纪律”。

### 必做动作

#### 4.1 给 coverage 一个明确阈值
在 CI 中加：
- `--cov-fail-under=95` 或更高
- 最好目标 >= 97%，如果做得到甚至更高

为什么不是空喊 100%：
- JMLR 写的是 close to 100%
- 你不需要伪装 100%，但要给 reviewer 一个硬门槛

#### 4.2 对 publicly exposed functionality 不做 coverage 特赦
如果 `leaderboard.py` 仍然属于 public surface，就不要 omit。  
如果你不想测它，就把它移出 public surface。

#### 4.3 公布 coverage badge / exact number
在 README 顶部增加 coverage badge。  
这样 reviewer 不用猜。

#### 4.4 增加 wheel install smoke test evidence
虽然 `cibuildwheel.toml` 已有 smoke test，这很好；  
但建议把 README / release notes 里写清楚：
- wheels are built/tested on Linux/macOS/Windows
- Python versions
- native extension optional fallback behavior

#### 4.5 补一套 import-path migration tests
如果你决定保留 `tsdecomp` compatibility：
- 专门测 alias 行为
- 但把这些测试放在 `compat` 分类，不要污染核心测试故事

### 涉及文件
- `.github/workflows/ci.yml`
- `.coveragerc`
- `README.md`
- `cibuildwheel.toml`
- tests/

### 完成标准
- CI 里有明确 fail-under
- README 有 coverage 数字
- coverage 不再对 public functionality 自相矛盾
- reviewer 可以直接看到“质量门槛是什么”

---

## Wave 5：补上 related software 的“硬比较证据”

### 目标
不只是说自己“定位不同”，而是证明**在明确的软件维度上有独立增量**。

### 必做动作

#### 5.1 重写 related software matrix
相关工作不能只写 scope，要写具体 axes：

- common decomposition result contract
- CLI for batch execution
- profiling workflow
- multivariate under same public model
- native kernels for selected methods
- explicit maturity/back-end taxonomy
- serialization for reproducible runs
- public website with tutorials and API
- release/install story
- focused depth within one family

然后把这些 axes 正面对比：
- `statsmodels`
- `PyEMD`
- `PyWavelets`
- `PySDKit`
- `SSALib`
- `sktime` / `vmdpy` lineage（针对 VMD）

#### 5.2 做一个小而公平的 runtime/features comparison
不要乱做大 benchmark。  
只选你最能 defend 的路径：

- `SSA`: De-Time vs SSALib（如果比较公平）
- `STL/MSTL`: De-Time wrapper path vs statsmodels（主要比较 workflow 一致性而不是性能）
- `EMD/CEEMDAN`: De-Time vs PyEMD（功能封装与 workflow，不强调 raw speed）
- `MVMD/MEMD`: De-Time optional path vs PySDKit（清楚声明 upstream dependency）

比较维度建议：
- install path
- result object consistency
- CLI availability
- batch/profile support
- runtime metadata
- whether outputs are immediately serializable
- optional multivariate support
- selected raw runtime (only where apples-to-apples)

#### 5.3 在 docs 增加“Why not just use X?”页面
新增 `docs/compare.md`：
- `Why not just use statsmodels?`
- `Why not just use PyEMD?`
- `Why not just use PySDKit?`
- `When to prefer SSALib over De-Time`

这会非常打 reviewer 的信任感：你不是在逃避对手，而是在告诉用户边界条件。

### 完成标准
- related-software section 不再回避 `PySDKit` 和 `SSALib`
- 对 `vmdpy` 的写法更新到 `sktime` 现状
- 对“你到底比现有软件多了什么”的回答能落到具体软件对象，而不是抽象定位

---

## Wave 6：重写 paper / cover letter，让它真正像 MLOSS software paper

### 目标
让 paper 的主线与实际公开软件状态一致。

### paper 应该怎么写

#### 正确主线
**De-Time is a workflow-oriented research software layer for reproducible time-series decomposition, not a claim of deeper or faster reimplementation of every included method family.**

#### 一定要明确写的句子
1. **不是新算法**
2. **不是替代所有 specialized libraries**
3. **主要贡献是 workflow / package design / result model / multivariate under same API / selective native kernels / release engineering**
4. **与 earlier benchmark artifact 的关系**
5. **为什么对 machine learning community relevant**

#### related software 中必须新增/强化
- `PySDKit`
- `SSALib`
- `sktime`/`vmdpy` lineage

#### cover letter 中必须更稳妥地写
- active user community 仍早期（诚实）
- 但公开 repo/release/docs/issue tracker 已准备好 review
- 若 adoption 弱，就靠 engineering quality / documentation / release hygiene / clear boundaries 扛

#### 一个重要新增：Machine-learning relevance paragraph
建议在 abstract 或 introduction 中加一段：
- decomposition is used in feature extraction, denoising, representation learning, interpretability, anomaly analysis, and preprocessing for downstream ML pipelines
- De-Time reduces software fragmentation for those workflows

### 完成标准
- paper 不再把 breadth 当 novelty
- paper 不再把 wrapper count 当贡献
- paper 的故事与实际 package boundary 一致
- reviewer 不再能轻松指出 “the paper overclaims relative to the codebase”

---

## 6. 具体到“网页”和“软件包”的修改清单

### A. 网页（docs / README / public GitHub surface）必须改的

#### 必改
- `mkdocs.yml`：移除 benchmark/agent 导航
- `docs/api.md`：只保留 public API/CLI
- `docs/examples.md`：不要突出 leaderboard
- `docs/tutorials/visual-benchmark.md`：删除或内迁
- `docs/agent-friendly.md`：从公开站点下线
- `docs/research-positioning.md`：加入 `SSALib`，把 `vmdpy` 改成 `sktime`/vmd lineage 写法
- `README.md`：弱化 `tsdecomp`，突出 `detime` canonical identity 与 release evidence
- 新增 `docs/compare.md`
- 新增 `docs/ml-workflows.md`

#### 强烈建议
- README 顶部增加：
  - coverage badge
  - PyPI badge（只有真的发布后）
  - release badge
- 把 “Project Files and Citation” 页面改成更短，不向普通用户展示太多 submission/internal material

---

### B. 软件包（src / packaging / release artifact）必须改的

#### 必改
- `src/detime/` 不再 import `tsdecomp`
- `src/tsdecomp/` 变 compatibility alias，而不是主体
- `src/synthetic_ts_bench/` 不进入 installable artifact
- `pyproject.toml` 清理 sdist include
- `MANIFEST.in` 清理 JMLR / agent materials
- `JMLR_MLOSS_CHECKLIST.md` 去掉 `tsdecomp` 命名残留
- 发布正式 GitHub release/tag

#### 强烈建议
- 创建 `compat/` 或单独 `tsdecomp-compat` 包，而不是在 reviewed artifact 中长期双主体共存
- 让 `detime` wheel smoke tests 成为主故事；`tsdecomp` 兼容 smoke test 变附属故事

---

## 7. Stop/Go 决策

### 现在：**STOP**
原因：
- canonical identity 未完成
- public docs 仍泄漏 artifact/agent/leaderboard
- package contents 仍不干净
- related software comparison 仍不足
- release/adoption evidence 太弱
- MLOSS fit 叙事还不够明确

### 什么时候可以进入“可投区”
至少满足以下条件后，才建议重新考虑提交：

1. `detime` 成为真实实现主体  
2. public docs 不再展示 benchmark / leaderboard / agent 页面  
3. sdist/wheel 不再包含 `synthetic_ts_bench` / `JMLR_*` / `AGENT_*`  
4. GitHub 有正式 release/tag，reviewed version 可冻结  
5. coverage threshold 公开且 enforce  
6. related software 中正面对上 `PySDKit`、`SSALib`、`sktime`/VMD story  
7. paper 增加 machine-learning relevance 段落  
8. 公开叙事里不再把 `tsdecomp` 当 equally first-class identity

---

## 8. 最后一句最难听但最有用的话

你现在最像的是：

> a serious extraction-and-packaging effort around a decomposition benchmark codebase

而不是：

> a fully stabilized standalone software contribution with clearly independent package identity

这句话听着难受，但它正是 reviewer 现在最可能的真实判断。  
你的下一轮修改，核心目标不是“再加一点文档”，而是**把这个判断扭转掉**。

---

## 9. 参考的公开来源（本次重审实际使用）

### JMLR / 审稿标准
- [JMLR MLOSS official page](https://www.jmlr.org/mloss/mloss-info.html)

### De-Time 公共仓库与文档源码
- [De-Time GitHub repo](https://github.com/systems-mechanobiology/De-Time)
- [README.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/README.md)
- [mkdocs.yml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/mkdocs.yml)
- [pyproject.toml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/pyproject.toml)
- [MANIFEST.in](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/MANIFEST.in)
- [PUBLISHING.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/PUBLISHING.md)
- [JMLR_MLOSS_CHECKLIST.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/JMLR_MLOSS_CHECKLIST.md)
- [docs/api.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/api.md)
- [docs/research-positioning.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/research-positioning.md)
- [docs/methods.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/methods.md)
- [docs/examples.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/examples.md)
- [docs/tutorials/visual-benchmark.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/tutorials/visual-benchmark.md)
- [docs/agent-friendly.md](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/docs/agent-friendly.md)
- [src/detime/__init__.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/__init__.py)
- [src/detime/core.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/core.py)
- [src/detime/registry.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/registry.py)
- [src/detime/cli.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/detime/cli.py)
- [src/tsdecomp/_native.py](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/src/tsdecomp/_native.py)
- [CI workflow](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.github/workflows/ci.yml)
- [wheels workflow](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.github/workflows/wheels.yml)
- [docs workflow](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/.github/workflows/docs.yml)
- [cibuildwheel.toml](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/cibuildwheel.toml)
- [cover letter draft](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/submission/cover_letter_jmlr_mloss.md)
- [paper draft](https://raw.githubusercontent.com/systems-mechanobiology/De-Time/main/submission/jmlr_mloss_software_paper_draft.md)

### 同类软件
- [statsmodels repo](https://github.com/statsmodels/statsmodels)
- [statsmodels STL docs](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.STL.html)
- [statsmodels MSTL docs](https://www.statsmodels.org/stable/generated/statsmodels.tsa.seasonal.MSTL.html)
- [PyEMD repo](https://github.com/laszukdawid/PyEMD)
- [PyEMD README](https://raw.githubusercontent.com/laszukdawid/PyEMD/master/README.md)
- [PyWavelets repo](https://github.com/PyWavelets/pywt)
- [PyWavelets README](https://raw.githubusercontent.com/PyWavelets/pywt/main/README.rst)
- [PyWavelets docs](https://pywavelets.readthedocs.io/en/latest/)
- [PySDKit repo](https://github.com/wwhenxuan/PySDKit)
- [PySDKit PyPI](https://pypi.org/project/PySDKit/)
- [SSALib repo](https://github.com/ADSCIAN/ssalib)
- [SSALib README](https://raw.githubusercontent.com/ADSCIAN/ssalib/main/README.md)
- [SSALib JOSS paper](https://joss.theoj.org/papers/10.21105/joss.08600)
- [vmdpy repo](https://github.com/vrcarva/vmdpy)
- [vmdpy README](https://raw.githubusercontent.com/vrcarva/vmdpy/master/README.md)
- [sktime repo](https://github.com/sktime/sktime)