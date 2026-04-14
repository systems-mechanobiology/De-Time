# De-Time 最终核对文件（JMLR MLOSS 提交前）

> 用法：提交前逐条打钩。任何一个 **硬阻断项** 未完成，都不建议提交。

---

## 一、硬阻断项（必须全勾）

- [ ] `src/detime` 已是主实现，不再是 shim
- [ ] `src/tsdecomp` 仅为 deprecated compatibility alias
- [ ] release artifact 不再包含 `src/synthetic_ts_bench/**`
- [ ] release artifact 不再包含 `submission/**`、`JMLR_*`、`AGENT_*` 等内部文件
- [ ] `detime --help` 不再公开 `run_leaderboard` / `merge_results` / `eval` / `validate` 等 benchmark 风格命令
- [ ] docs 顶层导航中不再前置 benchmark / agent / manuscript 风格页面
- [ ] cover letter 与 paper 中的所有 claims 与仓库现状一致
- [ ] 至少有一份与相关软件的 feature/runtime/support comparison
- [ ] coverage 有 fail-under 门槛
- [ ] wheel 与 sdist 都通过 smoke install

---

## 二、软件身份与命名

- [ ] 品牌统一写法：`De-Time`
- [ ] distribution 统一写法：`de-time`
- [ ] canonical import 统一写法：`detime`
- [ ] `tsdecomp` 只以 legacy alias 身份出现
- [ ] README、首页、install 页、paper 摘要、cover letter 中的 naming story 完全一致
- [ ] CLI help 中无命名冲突表述
- [ ] migration guide 已说明旧用户如何从 `tsdecomp` 迁移到 `detime`

---

## 三、发布工件边界

### 3.1 source tree
- [ ] `src/` 内只保留 installable package 所需代码
- [ ] benchmark / artifact 代码已移到 `benchmarks/`、独立 repo，或明确不打包

### 3.2 sdist
- [ ] `python -m build --sdist` 成功
- [ ] 解压检查 `dist/*.tar.gz` 后，不含 benchmark / submission / agent files
- [ ] `twine check dist/*` 通过

### 3.3 wheel
- [ ] 多平台 wheel build 成功
- [ ] 新环境安装 wheel 成功
- [ ] `import detime` 成功
- [ ] `detime --help` 成功
- [ ] 一个最小 decomposition 例子可运行

---

## 四、公共 API / CLI 表面

### 4.1 Python API
- [ ] `DecompResult` 文档清楚
- [ ] `DecompositionConfig` 文档清楚
- [ ] `decompose(series, config)` 是单一主入口
- [ ] univariate / multivariate / channelwise 的输入输出约定已文档化

### 4.2 CLI
- [ ] 主 CLI 只保留稳定命令：
  - [ ] `run`
  - [ ] `batch`
  - [ ] `profile`
- [ ] 公开 CLI help 简洁，不混入 benchmark orchestration
- [ ] 若 legacy/benchmark 命令仍存在，已标为 deprecated 或 internal-only

### 4.3 兼容层
- [ ] `tsdecomp` import 路径仍可用（若需要）
- [ ] 使用时有明确 deprecation warning
- [ ] 文档不再把它当成推荐路径

---

## 五、网站与文档

### 5.1 首页与安装
- [ ] 首页首段明确：不是新算法，是 workflow-oriented research software
- [ ] 首页明确：不替代所有 specialized libraries
- [ ] install 页明确：`pip install de-time`
- [ ] install 页明确：`import detime`
- [ ] install 页说明 wheel-first / source-fallback / optional extras

### 5.2 主导航
- [ ] Home
- [ ] Why De-Time
- [ ] Install
- [ ] Quickstart
- [ ] Choose a Method
- [ ] Methods
- [ ] API
- [ ] Architecture
- [ ] Tutorials
- [ ] Comparisons
- [ ] Migration from `tsdecomp`
- [ ] Contributing
- [ ] Citation / Release Notes

### 5.3 必要页面
- [ ] `why.md`
- [ ] `architecture.md`
- [ ] `comparisons.md`
- [ ] `migration.md`
- [ ] `reproducibility.md`

### 5.4 内容边界
- [ ] benchmark heatmap / leaderboard 页面不在主导航
- [ ] agent / internal tooling 页面不在主导航
- [ ] project files 页面不再像 submission inventory
- [ ] methods 页面有 maturity labels（flagship / wrapper / experimental）

### 5.5 文档构建
- [ ] `mkdocs build --strict` 通过
- [ ] 无 broken internal links
- [ ] 页面标题与叙事一致
- [ ] README 链接都指向正确 docs 页面

---

## 六、测试、CI、覆盖率

### 6.1 测试结构
- [ ] tests 按 core / flagship / wrappers / legacy / cli 分层
- [ ] 兼容层测试存在但不主导测试叙事
- [ ] 关键 flagship 方法有直接测试
- [ ] multivariate path 有测试

### 6.2 coverage
- [ ] coverage report 生成正常
- [ ] `fail_under` 已启用
- [ ] coverage scope 已说明
- [ ] 对外可陈述 coverage 水平

### 6.3 CI
- [ ] Linux 测试通过
- [ ] macOS 测试通过
- [ ] Windows 测试通过
- [ ] 多 Python 版本测试通过
- [ ] docs build job 通过
- [ ] wheel build job 通过
- [ ] smoke install job 通过

---

## 七、与同类软件的比较证据

### 7.1 需要正面比较的对象
- [ ] `statsmodels`
- [ ] `PyEMD`
- [ ] `PyWavelets`
- [ ] `PySDKit`
- [ ] `SSALib`

### 7.2 比较维度
- [ ] primary scope
- [ ] cross-family interface
- [ ] unified result object
- [ ] multivariate under same top-level API
- [ ] batch CLI
- [ ] profiling workflow
- [ ] native kernels
- [ ] docs / CI / testing posture
- [ ] community / openness posture

### 7.3 定量 evidence
- [ ] 至少一个 native vs python runtime comparison
- [ ] 至少一个 installability / platform support matrix
- [ ] 不把 scientific leaderboard 当成软件贡献主体

---

## 八、论文与 cover letter

### 8.1 论文标题 / 摘要 / 引言
- [ ] 明确“不是新算法”
- [ ] 明确“workflow-oriented research software layer”
- [ ] 明确“不是 benchmark paper”
- [ ] 明确“不是替代所有 specialized libraries”

### 8.2 Related software
- [ ] 不只做 scope 描述
- [ ] 有 feature/runtime/support comparison
- [ ] 对 `PySDKit` 和 `SSALib` 有正面回应
- [ ] 不夸大 wrapper methods 成熟度

### 8.3 Earlier artifact delta
- [ ] 有专门小节
- [ ] 有清晰 delta table
- [ ] 能说明为什么这不是“旧 artifact 换壳”

### 8.4 Cover letter
- [ ] 写明 reviewed version
- [ ] 写明 license
- [ ] 写明 repo / docs / issue tracker
- [ ] 如实说明 community/adoption 状态
- [ ] 写清与 earlier benchmark work 的关系
- [ ] 引用 software improvements / delta 文档（若需要）

### 8.5 一致性
- [ ] paper 中提到的命令、页面、模块在仓库中真实存在
- [ ] paper 中未承诺仓库没有的功能
- [ ] cover letter 与 paper 不互相矛盾
- [ ] paper 与 README / docs 首页叙事一致

---

## 九、开放性与可持续性

- [ ] `LICENSE` 正确
- [ ] `CITATION.cff` 正确
- [ ] `CHANGELOG.md` 更新到 reviewed version
- [ ] `CONTRIBUTING.md` 可用
- [ ] `SECURITY.md` 可用
- [ ] `ROADMAP.md` 可用
- [ ] issue tracker 公开
- [ ] 如适合，GitHub Discussions / issue templates 已配置
- [ ] reviewed version tag 已创建
- [ ] 如适合，Zenodo DOI 已更新

---

## 十、最终人工 reviewer 模拟

### 10.1 从零安装
- [ ] 陌生环境 `pip install de-time` 成功
- [ ] 按 docs quickstart 成功跑通
- [ ] 结果与文档一致

### 10.2 从 docs 理解项目
- [ ] reviewer 不读 paper，只看 docs，也能理解：
  - [ ] 软件是什么
  - [ ] 不是什么
  - [ ] 稳定核心方法是什么
  - [ ] 结果对象是什么
  - [ ] 与上游 specialized libraries 的关系是什么

### 10.3 从 paper 理解贡献
- [ ] reviewer 读完 paper，不会质疑：
  - [ ] “这是不是只是 benchmark artifact 的包装？”
  - [ ] “`detime` 是不是只是 `tsdecomp` 的 rename shim？”
  - [ ] “为什么不直接用 PySDKit / PyEMD / PyWavelets / statsmodels / SSALib？”
  - [ ] “你们的真正 software delta 是什么？”

### 10.4 提交前停止条件
- [ ] 所有硬阻断项已勾选
- [ ] 至少一位非作者同事按 docs 从零安装并成功运行
- [ ] 至少一位非作者同事通读 paper 后，能复述软件贡献边界
- [ ] reviewed source archive 与论文版本完全对应

---

## 十一、提交前一句话自检

> 如果一个刻薄的 reviewer 在 10 分钟内查看 repo 首页、docs 首页、`pyproject.toml`、`src/detime/__init__.py`、`docs/api.md` 和 paper 摘要，他是否会立刻认定这只是一个 benchmark artifact 的包装升级？

- [ ] 不会。现在它看起来像一个边界清楚的独立软件包。
