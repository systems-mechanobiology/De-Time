# De-Time 一致性审查与最终核对文件（2026-04-08）

> 用法：提交前逐项打勾。  
> 状态分为：
> - **PASS**：当前已经满足
> - **PARTIAL**：方向正确，但仍有残余问题
> - **FAIL**：当前仍构成明显 reviewer blocker

---

## 1. 身份与发布一致性

### 1.1 产品/分发/导入身份一致
- 状态：**PASS**
- 应一致的事实：
  - product brand = `De-Time`
  - distribution = `de-time`
  - preferred import = `detime`
  - legacy import = `tsdecomp`
- 当前检查：
  - README：一致
  - PUBLISHING：一致
  - pyproject：一致
  - docs/install：一致
- 备注：
  - 这是本轮最大的正向进步之一。

### 1.2 `tsdecomp` 仅为窄兼容层
- 状态：**PASS**
- 核对项：
  - `CMakeLists.txt` 只安装四个 `tsdecomp` compatibility files
  - `scripts/check_dist_contents.py` 只允许四个 `tsdecomp` files
  - `pyproject.toml` 的 sdist include 只包含四个 `src/tsdecomp` 文件
  - docs/release 文案均说明只保留顶层兼容
- 备注：
  - 当前构建规则与公开文案基本一致。

### 1.3 存在正式 release / tag / PyPI
- 状态：**FAIL**
- 当前问题：
  - GitHub Releases 为空
  - Tags 为空
  - `de-time` PyPI 仍未正式发布
- 风险：
  - JMLR reviewer 会质疑被审版本的固定性与 installability
  - adoption/community 证据更弱
- 必修动作：
  - 做正式 release，发布到 PyPI，更新 install 文案

---

## 2. 软件包边界一致性

### 2.1 sdist / wheel 边界与文案一致
- 状态：**PASS**
- 当前检查：
  - `pyproject.toml` 的 sdist include 已收缩
  - `MANIFEST.in` 排除 `submission/**`、`AGENT_*`、`JMLR_*`
  - `CMakeLists.txt` 与 `check_dist_contents.py` 一致
- 备注：
  - 相比上一轮，这个问题基本解决了。

### 2.2 benchmark-derived methods 不在主包中
- 状态：**PASS**
- 当前公开口径：
  - `DR_TS_REG`, `DR_TS_AE`, `SL_LIB` 已迁出主包
- 风险残余：
  - reviewer-facing 文档仍有个别旧提法（见 5.1 / 5.2）
- 必修动作：
  - 统一所有 reviewer-facing 文件

### 2.3 companion benchmark repo 已可核验
- 状态：**PARTIAL**
- 当前情况：
  - README 已声称存在 `de-time-bench`
  - 但需要确保有明确、可访问、可复现的 companion repo 链接与 scope split
- 风险：
  - 如果 reviewer 找不到 companion repo，会怀疑“只是口头切割”
- 必修动作：
  - 在 README/docs 中给出真实 URL
  - companion repo 至少有 scope README 与安装/复现路径

---

## 3. 公共网页与主叙事一致性

### 3.1 主导航是否已经去 benchmark 化
- 状态：**PASS**
- 当前 `mkdocs.yml` 主导航：
  - Why / Install / Quickstart / Methods / API / Architecture / Comparisons / Migration / Reproducibility
- 结论：
  - 主导航已经明显更像 standalone software package

### 3.2 docs/examples 是否仍有 benchmark residue
- 状态：**PARTIAL**
- 当前问题：
  - `docs/examples.md` 仍列出 `visual_leaderboard_walkthrough.py`
  - 仍保留 “Benchmark heatmap walkthrough”
  - 仍指向 `tutorials/visual-benchmark.md`
- 风险：
  - 虽然不在主导航里，但 reviewer 或用户仍可能看到
  - 与主包“不是 benchmark leaderboard package”的定位不完全一致
- 必修动作：
  - 清理 `docs/examples.md`
  - 将此类内容移动到 companion benchmark repo

### 3.3 install docs 是否诚实
- 状态：**PASS**
- 当前情况：
  - docs/install 与 README 都明确使用 GitHub install
  - 明确说明当前不是 PyPI 发布版本
  - 明确警告不要安装无关 `detime` PyPI 项目
- 备注：
  - 这点比之前诚实得多

---

## 4. 相关软件比较一致性

### 4.1 是否正面对比最危险对手
- 状态：**PASS**
- 当前比较页已纳入：
  - `PySDKit`
  - `SSALib`
  - `sktime`
  - `statsmodels`
  - `PyEMD`
  - `PyWavelets`
- 备注：
  - 这是本轮非常重要的修复

### 4.2 比较证据是否足够“审稿级”
- 状态：**PARTIAL**
- 当前优点：
  - 叙事已诚实很多
  - 还有一小段 runtime snapshot
- 当前不足：
  - 仍缺更系统的 feature/runtime/maturity matrix
  - 目前 performance snapshot 还偏单环境、单次风格
- 必修动作：
  - 新增更规范的 comparison table
  - 补一份可复现 performance evidence

---

## 5. reviewer-facing 文档一致性

### 5.1 `JMLR_MLOSS_CHECKLIST.md` 是否与当前边界一致
- 状态：**FAIL**
- 当前问题：
  - 仍写成 `tsdecomp`
  - 仍把 `DR_TS_REG` 写为 clearest core library method
- 风险：
  - reviewer 直接认为你边界没有稳定下来
- 必修动作：
  - 彻底按 De-Time 当前范围重写

### 5.2 `JMLR_SOFTWARE_IMPROVEMENTS.md` 是否与当前边界一致
- 状态：**FAIL**
- 当前问题：
  - 仍把 `DR_TS_REG` 写作 selected high-cost native-accelerated method
- 风险：
  - 与 README / comparisons / current package boundary 冲突
- 必修动作：
  - 改成 retained flagship path only

### 5.3 `JMLR_SUBMISSION_CHECKLIST.md` 是否基本正确
- 状态：**PASS**
- 当前优点：
  - 已使用 De-Time 身份
  - 已承认 strongest/weakest framing
- 后续动作：
  - 与其他两份 reviewer docs 对齐

---

## 6. 工程质量证据一致性

### 6.1 CI / docs / wheels 是否齐全
- 状态：**PASS**
- 当前具备：
  - cross-platform tests
  - coverage job
  - docs strict build
  - wheels / sdist / smoke install
  - publish workflow
- 备注：
  - 工程面已明显进入可审状态

### 6.2 coverage 口径是否透明
- 状态：**PARTIAL**
- 当前事实：
  - `fail_under = 90`
  - 但 `.coveragerc` 明确 omit 若干 wrappers / CLI / viz / I/O / methods
- 风险：
  - 若在 paper/README 中不解释，reviewer 会误读为 whole-package coverage
- 必修动作：
  - 明确写“core-plus-flagship surface” coverage

### 6.3 当前 coverage snapshot 是否作为事实被合理使用
- 状态：**PARTIAL**
- 当前问题：
  - README 中写 `91.40%`
  - 需要补充该数字的边界与生成方式
- 必修动作：
  - 在 docs/testing 或 reproducibility 页面解释口径

---

## 7. 社区与采用证据

### 7.1 active user community 是否已有公开证据
- 状态：**FAIL**
- 当前公开状态：
  - 0 stars
  - 0 forks
  - 0 issues
  - 0 PRs
- 风险：
  - JMLR MLOSS 明确要求 cover letter 说明 active user community
- 必修动作：
  - release 后尽快补最小公开使用证据
  - 开 issue templates / discussions
  - 如有外部试用者，形成可验证 evidence

### 7.2 openness / contribution path 是否已具备
- 状态：**PASS**
- 当前具备：
  - public repo
  - issue tracker
  - CONTRIBUTING
  - CODE_OF_CONDUCT
  - SECURITY
- 备注：
  - 结构上是开放的；缺的是活跃度

---

## 8. agent-friendly / token-efficiency 一致性

### 8.1 是否已有第一代 agent-friendly surface
- 状态：**PASS**
- 当前具备：
  - `AGENT_MANIFEST.json`
  - `AGENT_INPUT_CONTRACT.md`
  - `ENTRYPOINTS.md`
  - `START_HERE.md`
  - predictable artifact contract
- 备注：
  - 这使它已经不是“纯人类 README 软件”

### 8.2 是否达到 2026 agent-native 标准
- 状态：**FAIL**
- 当前缺失：
  - MCP server
  - registry-ready interface
  - JSON schemas
  - toolset slicing
  - metadata-only / summary-only low-token modes
- 风险：
  - 只能算 agent-legible，不算 protocol-native
- 必修动作：
  - 做 MCP + schema + summary/meta-only outputs

### 8.3 是否已经“比较省 token”
- 状态：**PARTIAL**
- 当前优点：
  - entrypoint 少
  - input contract 清楚
  - artifacts predictable
- 当前不足：
  - 缺少 summary-only / meta-only / field slicing / schema introspection
- 必修动作：
  - 增加 CLI/API 的裁剪输出模式

---

## 9. 与两条研究主线的一致性

### 9.1 与 decomposition benchmark 稿子的一致性
- 状态：**PARTIAL**
- 当前优点：
  - De-Time 已可以成为 benchmark 的 reusable front-end
- 当前不足：
  - benchmark capability map / diagnostics 还未回流到主包
- 后续动作：
  - 增加 method recommender 与 failure diagnostics

### 9.2 与 Dec-SR 稿子的一致性
- 状态：**PARTIAL**
- 当前优点：
  - common result contract 已具备作为 Dec-SR 前端的潜力
- 当前不足：
  - 缺少直接 handoff contract（to PySR / ND2）
- 后续动作：
  - 增加 downstream discovery bridge

---

## 10. 提交前 stop/go 决策

## JMLR MLOSS
### 当前状态：**NO-GO**
### 变成 GO 的必要条件
- [ ] 正式 release / tag / PyPI
- [ ] `JMLR_MLOSS_CHECKLIST.md` 重写
- [ ] `JMLR_SOFTWARE_IMPROVEMENTS.md` 重写
- [ ] `docs/examples.md` 清理 benchmark residue
- [ ] companion benchmark repo 可核验
- [ ] comparison evidence 再硬化
- [ ] coverage boundary 写清楚
- [ ] 至少有最小 adoption/community evidence

## Nature Machine Intelligence（软件本体）
### 当前状态：**NO-GO**
### 原因
- 软件本体不足以构成 NMI 所需的概念推进
- 应转为 benchmark + Dec-SR + scientific claim 组合叙事

## agent-native v1
### 当前状态：**NO-GO**
### 变成 GO 的必要条件
- [ ] MCP server
- [ ] JSON schema
- [ ] summary/meta-only outputs
- [ ] toolset slicing

---

## 11. 最终一句话判定

### 当前快照是什么
**一个已经明显成型的 standalone research software package。**

### 当前快照还不是什么
**还不是 release-grade、adoption-backed、agent-native 的下一代 decomposition platform。**

### 接下来最关键的三件事
1. **做真 release**
2. **把 reviewer-facing 文档彻底统一**
3. **把 benchmark residue 与 agent-native 方向分别做干净**
