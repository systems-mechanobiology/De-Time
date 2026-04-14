# De-Time 最终核对文件（JMLR MLOSS v3）

> 用法：提交前逐项勾。  
> 规则：**Hard blockers 有任何一项未完成，就不要提交。**

---

## A. Hard blockers（任何一项未完成 = STOP）

### 软件身份
- [ ] `detime` 已经是**真实实现主体**，而不是 `tsdecomp` 的 re-export shim
- [ ] `src/detime/` 中不再存在系统性 `from tsdecomp ...` 依赖
- [ ] `tsdecomp` 已降为 compatibility alias 或单独 compat path
- [ ] `PUBLISHING.md` 已改成 `detime` canonical story
- [ ] `JMLR_MLOSS_CHECKLIST.md` 等 reviewer-facing 文件中没有 `tsdecomp` 主体残留

### 公共网页 / docs
- [ ] `mkdocs.yml` 主导航中已删除 `Visual Benchmark Heatmaps`
- [ ] `mkdocs.yml` 主导航中已删除 `Agent Tools`
- [ ] `docs/api.md` 只展示真正 public 的命令/API
- [ ] `docs/examples.md` 不再把 leaderboard walkthrough 当 public showcase
- [ ] `docs/tutorials/visual-benchmark.md` 已下线、内迁或与 public docs 脱钩
- [ ] public docs 首页看起来像 library site，而不是 artifact portal

### 包边界 / source distribution
- [ ] `src/synthetic_ts_bench` 不再进入 sdist / reviewed artifact
- [ ] `pyproject.toml` 的 sdist include 已清理 `synthetic_ts_bench`
- [ ] `pyproject.toml` / `MANIFEST.in` 已移除 `JMLR_*`
- [ ] `pyproject.toml` / `MANIFEST.in` 已移除 `AGENT_*`
- [ ] 构建后的 sdist 解压后看起来是“干净的软件包”，而不是研究仓库 dump

### release / reviewed version
- [ ] GitHub 仓库已有正式 release
- [ ] GitHub 仓库已有正式 tag
- [ ] reviewed version 已在 README / paper / cover letter 中统一
- [ ] `CITATION.cff` 对应的是冻结后的 reviewed version

### 相关工作与 MLOSS 适配
- [ ] related software 已正面对比 `PySDKit`
- [ ] related software 已正面对比 `SSALib`
- [ ] `vmdpy` 的写法已更新为 `sktime`/VMD lineage 现状
- [ ] paper / docs 已明确说明 De-Time 对 machine learning community 的 relevance
- [ ] paper 已明确说明：De-Time **不是新算法**，也**不是替代所有 specialized libraries**

---

## B. 软件质量与工程证据

### 测试 / coverage
- [ ] CI 中有明确 `--cov-fail-under` 阈值
- [ ] coverage 数字公开可见（badge 或 docs/README）
- [ ] coverage story 与 public surface 一致
- [ ] 若 `leaderboard.py` 仍属 public surface，则已纳入覆盖测试
- [ ] 若 `leaderboard.py` 不再属 public surface，则 docs/API/examples 已完全下线该功能

### CI / wheel / install
- [ ] tests 在 Linux / macOS / Windows 跑过
- [ ] 支持的 Python 版本在 CI 中被覆盖
- [ ] wheel 构建后有 smoke test
- [ ] README 的安装路径与真实 release path 一致
- [ ] native extension optional fallback 路径在文档中解释清楚

### 开发者开放性
- [ ] `CONTRIBUTING.md` 仍有效且与当前 repo 结构一致
- [ ] `CODE_OF_CONDUCT.md` 存在
- [ ] `SECURITY.md` 存在
- [ ] issue tracker 与 repo URLs 正确
- [ ] docs / API / examples 与当前代码真实一致

---

## C. 网页与 README 体验

### README 首屏
- [ ] 首屏只突出 `De-Time` / `detime`
- [ ] 首屏不再把 `tsdecomp` 当 first-class identity
- [ ] 首屏没有 benchmark artifact / leaderboard / agent 的视觉暗示
- [ ] README 顶部 badge 信息可信且不过度承诺
- [ ] README 中的安装命令、导入命令、CLI 命令全部经过实际测试

### docs 信息架构
- [ ] Quickstart 足够短，首次成功路径明确
- [ ] Install 页没有过多历史兼容叙事
- [ ] API 页只写 public surface
- [ ] Methods Atlas 清楚区分 flagship / built-in / wrapper / optional backend
- [ ] `research-positioning.md` 是 current、诚实、不过时的
- [ ] 至少有一个 ML-facing tutorial / page
- [ ] 至少有一个 honest comparison page（如 `Why not just use X?`）

---

## D. 相关软件对比：提交前必须能回答的 10 个问题

- [ ] 为什么不直接用 `statsmodels`？
- [ ] 为什么不直接用 `PyEMD`？
- [ ] 为什么不直接用 `PyWavelets`？
- [ ] 为什么不直接用 `PySDKit`？
- [ ] 为什么不直接用 `SSALib`？
- [ ] De-Time 的 multivariate 增量到底是什么，而不是简单套 `PySDKit`？
- [ ] 你在 `SSA` 上到底比 `SSALib` 多什么？
- [ ] 你在 classical decomposition 上为什么不是重复 `statsmodels`？
- [ ] 你在 VMD 相关叙事上为什么还提 `vmdpy`，而不是 `sktime` 现状？
- [ ] 如果 reviewer 说 “this is mostly workflow packaging”, 你的正面回答是什么？

---

## E. Paper / cover letter 最终核对

### Paper
- [ ] 标题没有过度宣称
- [ ] 摘要明确 software contribution，而不是算法 novelty
- [ ] introduction 说明 fragmentation + workflow problem
- [ ] related software 正面对上 `PySDKit` / `SSALib`
- [ ] implementation section 与真实 repo 结构一致
- [ ] relationship-to-earlier-artifact section 清楚写明边界变化
- [ ] limitations section 诚实写 wrapper / optional backends / maturity heterogeneity
- [ ] machine-learning relevance 有单独段落
- [ ] 全文没有把 breadth 写成 novelty 本身
- [ ] 全文没有把 wrapper count 写成贡献本身

### Cover letter
- [ ] 明确说明 intended for JMLR MLOSS
- [ ] license / project URL / reviewed version 都已写清楚
- [ ] adoption 证据诚实但不空
- [ ] 若 adoption 弱，已用 release/docs/CI/quality gates 补足 reviewer 可审信息
- [ ] 与 benchmark paper 的关系写清楚
- [ ] reviewers/AE suggestions（若要给）准备好

---

## F. 人工 spot-check（提交前最后 20 分钟）

- [ ] 从一个全新环境执行 README install 命令
- [ ] 跑一个最短 Python quickstart
- [ ] 跑一个最短 CLI quickstart
- [ ] 打开 GitHub Pages 首页，确认无 benchmark / agent 泄漏
- [ ] 打开 API 页，确认无 leaderboard / eval / validate 泄漏
- [ ] 构建一次 sdist，解压后人工确认没有 `synthetic_ts_bench`
- [ ] 构建一次 wheel，确认 `detime` 能 import
- [ ] 检查 `tsdecomp` 兼容路径是否只在 migration/compat context 出现
- [ ] 抽查 paper 中 3 处最容易被 reviewer 抓住的表述，确认没有过度 claim
- [ ] 确认版本号、tag、release notes、paper、cover letter 全部一致

---

## G. 最后的 Stop / Go 结论

### 只有当下面 5 条都满足时，才允许 GO
- [ ] `detime` canonical identity 已完成
- [ ] public docs 不再泄漏 benchmark / agent / leaderboard
- [ ] reviewed artifact 的包边界已清理干净
- [ ] related software 对 `PySDKit` / `SSALib` / `sktime` 现状已处理到位
- [ ] paper/cover letter 的 software story 与代码现实完全一致

### 否则
- [ ] **STOP，继续修改，不提交**