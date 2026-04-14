# De-Time Codex Task List

> 目标：把当前仓库从“整理过的 benchmark-oriented repository”改造成“JMLR MLOSS 可审的独立软件包”。  
> 约束：`De-Time` 为品牌名，distribution 保持 `de-time`，canonical import 为 `detime`，`tsdecomp` 只保留为过渡 alias。  
> 原则：先改 package identity 和 release boundary，再改 docs，再补 CI/release 证据，最后重写 paper。

---

## A. 总执行规则

- [ ] 不新增含糊的 public surface；任何新命令、新页面都必须能回答“这是不是核心软件能力？”
- [ ] 不把 benchmark orchestration 继续塞进 installable package。
- [ ] 不把 `tsdecomp` 当作并列品牌维护；只作为过渡兼容层。
- [ ] 所有文档、README、CLI help、paper、cover letter 叙事必须一致：
  - 品牌：`De-Time`
  - distribution：`de-time`
  - canonical import：`detime`
  - legacy alias：`tsdecomp`

---

## B. Epic 1 — Namespace / package identity surgery

### B1. 让 `detime` 变成主实现
**目标**：`src/detime` 不再只是 re-export shim。

- [ ] 将 `src/tsdecomp` 中真实实现迁移到 `src/detime`
- [ ] 把内部 imports 统一改成 `detime.*`
- [ ] 保持 public API 不变：`DecompResult`, `DecompositionConfig`, `MethodRegistry`, `decompose`, native capability helpers
- [ ] 在 `src/detime/__init__.py` 中移除 “thin compatibility-first shim” 文案
- [ ] 确保 `src/detime/cli.py` 调用的是 `detime.cli.main` 本地实现，而不是转发给 `tsdecomp`

**建议触及文件**
- `src/detime/**/*.py`
- `src/tsdecomp/**/*.py`
- `tests/test_branding_imports.py`
- 其他所有使用 `from tsdecomp ...` 的源码文件

**验收**
- [ ] `grep -R "from tsdecomp" src/detime` 无结果
- [ ] `python -c "import detime; print(detime.DecompositionConfig)"` 正常
- [ ] `python -m detime --help` 正常

### B2. 将 `tsdecomp` 降级为 deprecated alias
**目标**：兼容旧用户，但不再维持双主路径。

- [ ] `src/tsdecomp/__init__.py` 改成纯 re-export
- [ ] import `tsdecomp` 时发 `DeprecationWarning`
- [ ] CLI `python -m tsdecomp` 或 `tsdecomp` script 也打印 deprecation notice
- [ ] 文档中所有示例统一改成 `detime`
- [ ] 保留最小兼容测试，但标注为 legacy

**验收**
- [ ] `import tsdecomp` 仍可用
- [ ] warning 信息明确给出迁移方向
- [ ] README 和 docs 不再把 `tsdecomp` 写成并列身份

### B3. 统一 distribution / import 文案
**目标**：彻底消除名字歧义。

- [ ] README 首屏改成：`pip install de-time` / `import detime`
- [ ] docs 首页、install 页、migration 页、paper 摘要全部同步
- [ ] CLI `--help` 里显示品牌与安装提示
- [ ] 显式说明 `detime` 这个 import 名称对应 distribution `de-time`

**验收**
- [ ] 仓库内搜索 `pip install detime` 不再出现
- [ ] 仓库内搜索 “preferred import `tsdecomp`” 不再出现
- [ ] 所有公开页面的 naming story 完全一致

---

## C. Epic 2 — 拆分 benchmark artifact 与 installable software

### C1. 将 `src/synthetic_ts_bench` 移出 installable package
**目标**：`pip install de-time` 安装的软件包不再包含 benchmark artifact 代码。

- [ ] 将 `src/synthetic_ts_bench` 移动到顶层 `benchmarks/` 或 `research_artifacts/`
- [ ] 若代码必须保留 import path，则改为独立 companion package 或局部脚本
- [ ] 更新任何依赖该路径的 examples / docs / CI

**建议触及文件**
- `src/synthetic_ts_bench/**`
- `examples/**`
- `docs/tutorials/visual-benchmark.md`
- 任何 benchmark helper imports

**验收**
- [ ] `pip install -e .` 后 `import synthetic_ts_bench` 失败或不推荐
- [ ] wheel / sdist 内不再含 benchmark package
- [ ] benchmark code 仍可在顶层目录单独运行

### C2. 清理 `pyproject.toml` 的 sdist include
**目标**：发布工件只包含软件本体和必要 supporting files。

- [ ] 移除 sdist include 中的：
  - `src/synthetic_ts_bench/**/*.py`
  - `JMLR_*`
  - `submission/**`
  - `AGENT_*`（若不属于软件本体）
- [ ] 保留必要的：
  - `src/detime/**`
  - `src/tsdecomp/**`（仅兼容层）
  - `native/**`
  - `tests/**`
  - `docs/**`
  - `examples/**`
  - `README`, `LICENSE`, `CITATION.cff`, `CHANGELOG`, `CONTRIBUTING`, `SECURITY`

**验收**
- [ ] `python -m build --sdist` 成功
- [ ] 解压 `dist/*.tar.gz` 后人工检查，不再包含 benchmark/submission/agent files
- [ ] `twine check dist/*` 通过

### C3. benchmark-only helpers 退出公共软件表面
**目标**：不再让 reviewer 误认为 leaderboard / merge 是核心软件能力。

- [ ] 将 `leaderboard.py`, `bench_config.py` 等迁往 `benchmarks/`
- [ ] 如必须保留，改为 internal module，不进入 `detime` 顶层表面
- [ ] 从 docs API 页面移除 benchmark-only 命令与模块
- [ ] 若保留 benchmark CLI，单独创建 `detime-bench` 或 `python -m detime_bench`

**验收**
- [ ] `from detime import ...` 不再暴露 benchmark helpers
- [ ] `docs/api.md` 不再列出 benchmark orchestration 命令
- [ ] `detime --help` 只展示稳定主路径

---

## D. Epic 3 — 公开 CLI 与 API 收缩为“软件贡献”

### D1. 公开 CLI 只保留稳定命令
**目标**：公开 CLI 只展示 `run`, `batch`, `profile` 及少量辅助命令。

- [ ] `detime run`
- [ ] `detime batch`
- [ ] `detime profile`
- [ ] 可选新增：`detime methods`, `detime doctor`, `detime version`

**应移除或隐藏**
- [ ] `eval`
- [ ] `validate`
- [ ] `run_leaderboard`
- [ ] `merge_results`

**验收**
- [ ] `detime --help` 输出简洁、聚焦
- [ ] CLI 文档与帮助页一致
- [ ] 旧命令若仍存在，则显示 deprecation / internal-only 提示

### D2. 稳定 result serialization 与 schema 文档
**目标**：突出 De-Time 的结果契约，而不是方法列表。

- [ ] 文档化 `DecompResult` schema
- [ ] 给出 univariate / multivariate 输出形状例子
- [ ] 明确 `components` 与 `meta` 的语义边界
- [ ] 增加 JSON/CSV/NumPy 保存示例（若已支持）

**验收**
- [ ] reviewer 不看源码也能明白结果对象结构
- [ ] 文档能解释 multivariate 结果如何表示

---

## E. Epic 4 — 网站与文档 IA 重构

### E1. 重写 `mkdocs.yml`
**目标**：主导航只保留 reviewer / user 应看到的内容。

**建议新导航**
- Home
- Why De-Time
- Install
- Quickstart
- Choose a Method
- Methods
- API
- Architecture
- Tutorials
- Comparisons
- Migration from `tsdecomp`
- Contributing
- Citation / Release Notes

**从主导航移除**
- [ ] `Visual Benchmark Heatmaps`
- [ ] `Agent Tools`
- [ ] `Project Files and Citation`（拆分重写）
- [ ] 任何 manuscript / internal tooling 页面

**验收**
- [ ] docs 首页到 API 的路径不经过 benchmark 页面
- [ ] 顶层导航叙事单一：软件，而不是 artifact

### E2. 新增关键页面
- [ ] `docs/why.md`
- [ ] `docs/architecture.md`
- [ ] `docs/comparisons.md`
- [ ] `docs/migration.md`
- [ ] `docs/reproducibility.md`

**每页最低要求**
- `why.md`：问题定义、贡献边界、非目标
- `architecture.md`：模块图、数据流、backend story
- `comparisons.md`：与 `statsmodels`、`PyEMD`、`PyWavelets`、`PySDKit`、`SSALib` 的对比
- `migration.md`：`tsdecomp` 到 `detime` 迁移
- `reproducibility.md`：平台、wheel/source build、optional extras、known limitations

**验收**
- [ ] docs build --strict 通过
- [ ] 新页面均出现在导航中
- [ ] 首页、README、paper 中都能链接到这些页面

### E3. 重写首页与安装页
**目标**：一眼看出软件定位。

- [ ] 首页首段明确：
  - 不是新算法
  - 是 workflow-oriented research software
  - 核心是 unified result/config contract
- [ ] install 页明确：
  - `pip install de-time`
  - `import detime`
  - wheel-first
  - source build fallback
  - optional `multivar` extra

**验收**
- [ ] 首页不再把 benchmark/heatmap 当成主吸引点
- [ ] install 页读完后，用户不会搞混 brand / distribution / import

### E4. Methods Atlas 与 tutorials 重新分层
**目标**：突出 stable core，降低 wrapper / experiment 的噪声。

- [ ] `docs/methods.md` 中给每种方法加 maturity badge：
  - flagship
  - stable wrapper
  - experimental wrapper
  - legacy / benchmark-support
- [ ] tutorials 首页优先展示：
  - `STD`
  - `STDR`
  - `SSA`
  - `MSSA`
- [ ] benchmark heatmap tutorial 移到 developer / appendix 区域

**验收**
- [ ] 新用户不会先看到 leaderboard 页面
- [ ] reviewer 能快速理解 strongest current path

### E5. （可选）切换到更适合软件项目的 docs theme
- [ ] 评估 `mkdocs-material`
- [ ] 加 search / admonitions / tabs
- [ ] 加 badges：build, coverage, wheel, PyPI
- [ ] 保持内容优先，不做视觉花活

**验收**
- [ ] 页面结构更清晰
- [ ] 文档网站具备典型软件项目可读性

---

## F. Epic 5 — Testing / CI / release hardening

### F1. coverage threshold enforcement
**目标**：从“生成 coverage 报告”升级到“coverage 是门槛”。

- [ ] 在 `.coveragerc` 或 pytest-cov 参数中加入 fail-under
- [ ] 第一版先设 90，后续拉到 95+
- [ ] 将核心 coverage 口径聚焦 `detime`
- [ ] legacy alias 单独测试，不拖累主包 coverage 叙事

**验收**
- [ ] coverage 未达阈值时 CI fail
- [ ] README / docs 有 coverage badge
- [ ] 有一份公开说明 coverage scope

### F2. wheel smoke test
**目标**：证明 wheel 不只是能 build，还能 install and run。

- [ ] wheels build 后新增 smoke-test job
- [ ] 测试项：
  - `import detime`
  - `detime --help`
  - 一个最小 univariate decomposition
  - 一个 native-backed path
- [ ] Linux 上再测 `pip install ".[multivar]"` 的最小 optional backend 路径

**验收**
- [ ] wheel smoke tests 在支持平台通过
- [ ] docs 中可声明 wheel-first install story

### F3. sdist smoke install + metadata checks
- [ ] `python -m build --sdist`
- [ ] 新环境从 sdist 安装
- [ ] `twine check`
- [ ] 验证 `pip show de-time` 元数据
- [ ] 验证安装后 package contents 正确

**验收**
- [ ] sdist 可以独立安装
- [ ] 没有 submission / benchmark junk files

### F4. 测试分层与 fixture 收缩
- [ ] 建立 `tests/core/`
- [ ] 建立 `tests/flagship/`
- [ ] 建立 `tests/wrappers/`
- [ ] 建立 `tests/legacy/`
- [ ] 建立 `tests/cli/`
- [ ] benchmark artifact 若保留，单独 `tests/benchmarks/`

**验收**
- [ ] test suite 结构本身可反映软件边界
- [ ] reviewer 看 tests 目录就知道主包与兼容层的关系

---

## G. Epic 6 — Comparative evidence for paper + website

### G1. 生成 competitor feature matrix
**目标**：补齐 JMLR 要求的 features comparison。

**比较对象**
- [ ] `statsmodels`
- [ ] `PyEMD`
- [ ] `PyWavelets`
- [ ] `PySDKit`
- [ ] `SSALib`

**比较维度**
- [ ] primary scope
- [ ] cross-family interface
- [ ] common result object
- [ ] multivariate under same top-level API
- [ ] batch CLI
- [ ] profiling workflow
- [ ] native kernels
- [ ] docs website
- [ ] CI / tests / coverage
- [ ] maturity labeling

**输出位置**
- `docs/comparisons.md`
- `submission/jmlr_mloss_software_paper_draft.md`

### G2. 补 native vs python runtime 数据
**目标**：补齐最小可辩护的 performance evidence。

**建议方法**
- [ ] `STD`
- [ ] `STDR`
- [ ] `SSA`
- [ ] `DR_TS_REG`（仅当其保留在主包时）

**建议实验维度**
- [ ] series length scaling
- [ ] repeat runs / median runtime
- [ ] native vs python fallback
- [ ] 单机固定环境说明

**输出**
- [ ] 一个 docs 页面
- [ ] paper 中一张简洁图/表
- [ ] benchmark code 与软件 paper 分离，不混成大 leaderboard

### G3. 生成 earlier artifact delta table
**目标**：把“不是旧 artifact 换壳”这件事写硬。

- [ ] 建表比较：
  - repo boundary
  - canonical import
  - public CLI
  - installable artifact contents
  - docs posture
  - CI / release posture
  - multivariate integration
  - native kernels

**输出**
- `docs/why.md`
- `submission/jmlr_mloss_software_paper_draft.md`
- `submission/cover_letter_jmlr_mloss.md`

---

## H. Epic 7 — Paper / cover letter rewrite

### H1. 重写摘要与引言
- [ ] 明确“不是新算法”
- [ ] 明确“workflow-oriented research software layer”
- [ ] 明确“not a replacement for every specialized library”
- [ ] 清楚说 earlier artifact → standalone package 的 delta

### H2. 重写 related software
- [ ] 增加对 `PySDKit` 和 `SSALib` 的正面比较
- [ ] 避免把 method count 当作贡献
- [ ] 避免夸大 wrapper methods 的成熟度

### H3. 重写 implementation / quality sections
- [ ] 直接讲 `DecompResult`, `DecompositionConfig`, registry, backend story
- [ ] 给 architecture figure
- [ ] 给 CI / release / docs / coverage 的证据
- [ ] 把 benchmark-specific 内容降到最低

### H4. 重写 cover letter
- [ ] 保留诚实边界
- [ ] 补 active user community 与 openness 的可证据内容
- [ ] 加 delta table / improvements note 引用
- [ ] 所有 claims 与 repo 状态一一对应

**验收**
- [ ] paper 与 README / docs / code 不打架
- [ ] reviewer 不会在第一页就质疑“你到底投的是啥”

---

## I. Epic 8 — Community / openness hygiene

### I1. GitHub openness
- [ ] issue templates
- [ ] feature request template
- [ ] bug report template
- [ ] GitHub Discussions（若适合）
- [ ] CODEOWNERS（可选）
- [ ] release notes 规范化

### I2. Citation / archival
- [ ] 检查 `CITATION.cff`
- [ ] 绑定 Zenodo DOI（如可行）
- [ ] reviewed version tag 固定
- [ ] 归档源码与论文版本一致

### I3. Release policy
- [ ] 采用语义化版本
- [ ] 在 CHANGELOG 里明确 breaking changes
- [ ] 记录 `tsdecomp` deprecation timeline

---

## J. 建议执行顺序（给 Codex 的实际顺序）

### Wave 1 — 必做 blocker
- [ ] B1
- [ ] B2
- [ ] B3
- [ ] C1
- [ ] E1

### Wave 2 — docs & release posture
- [ ] D1
- [ ] D2
- [ ] D3
- [ ] F2
- [ ] F3

### Wave 3 — evidence & manuscript
- [ ] G1
- [ ] G2
- [ ] G3
- [ ] H1
- [ ] H2
- [ ] H3
- [ ] H4

### Wave 4 — polish
- [ ] E4
- [ ] I1
- [ ] I2
- [ ] I3

---

## K. 最终自动化检查命令（建议加入 CI 或 release checklist）

```bash
# style / imports
grep -R "from tsdecomp" src/detime || true

# test suite
python -m pytest tests -q

# coverage
python -m pytest tests --cov=detime --cov=tsdecomp --cov-report=term-missing

# docs
mkdocs build --strict

# build artifacts
python -m build
twine check dist/*

# smoke install from wheel
python -m venv /tmp/detime-wheel-test
source /tmp/detime-wheel-test/bin/activate
pip install dist/*.whl
python -c "import detime; print(detime.DecompositionConfig)"
detime --help
```

---

## L. 任务完成判据（Codex 必须全部满足）

- [ ] `detime` 为真实主实现，不再是 shim
- [ ] `tsdecomp` 为 warning-bearing legacy alias
- [ ] benchmark code 不在 installable package 内
- [ ] public CLI 收缩为稳定路径
- [ ] docs 主导航无 benchmark / agent / submission 气味
- [ ] coverage 有门槛
- [ ] wheel / sdist 有 smoke tests
- [ ] comparison page 和 paper comparison table 已生成
- [ ] paper/README/docs naming story 完全统一
- [ ] JMLR reviewer 下载 reviewed source 后，看到的是软件，而不是投稿工作目录
