# De-Time 一致性审查与最终核对文件（v6）

用途：提交 JMLR software paper 前的 stop / go checklist。  
规则：凡是标记为 **BLOCKER** 的项目若未通过，不建议提交。

---

## 一、Public identity 一致性

### 1.1 canonical package
- [ ] **BLOCKER** README 明确写 canonical import = `detime`
- [ ] **BLOCKER** docs 全站没有把 `tsdecomp` 当作主实现
- [ ] `tsdecomp` 明确标为 deprecated compatibility alias
- [ ] deprecation horizon 已公开说明

### 1.2 distribution / install naming
- [ ] **BLOCKER** distribution name 在 README / docs / release / paper 中完全一致
- [ ] **BLOCKER** 所有 `pip install ...` 说明与真实公开状态一致
- [ ] `pyproject.toml` 与 public docs 的 package name 一致

### 1.3 versioning
- [ ] Git tag / GitHub release / package version 一致
- [ ] docs 中提到的 latest version 与 release state 一致
- [ ] submission 中的 version to review 与公开 release 一致

---

## 二、Install / release 真值核查

### 2.1 install path
- [ ] **BLOCKER** reviewer 按 docs 可以真实安装成功
- [ ] **BLOCKER** 若写 PyPI，则 PyPI 页面真实存在且可安装
- [ ] 如果未写 PyPI，则 docs 没有任何“已发布到 PyPI”暗示

### 2.2 release artifacts
- [ ] GitHub release 存在
- [ ] wheels / sdist 存在
- [ ] wheel / sdist smoke install 通过
- [ ] dist-content 检查通过

### 2.3 PUBLISHING truthfulness
- [ ] `PUBLISHING.md` 描述与当前 release reality 一致
- [ ] release notes 没有超出事实的表述

---

## 三、Package boundary 与 artifact hygiene

### 3.1 installable core
- [ ] **BLOCKER** installable package 中不再混入 benchmark artifact 文件
- [ ] **BLOCKER** installable package 中不再混入 reviewer-only / submission-only 文件
- [ ] sdist include/exclude 规则已核对

### 3.2 docs boundary
- [ ] 主导航不再公开 benchmark / leaderboard / internal tooling 页面
- [ ] 若存在 companion benchmark 页面，其位置与语气明确为 companion
- [ ] “not a benchmark artifact” 的陈述与包内容相匹配

### 3.3 companion repo relationship
- [ ] software repo 与 benchmark repo 的关系写清楚
- [ ] software paper 中 companion relation 单独说明
- [ ] reviewer bundle 有 dedicated explanation

---

## 四、测试与质量证据

### 4.1 coverage
- [ ] **BLOCKER** coverage 数字有清晰分母说明
- [ ] **BLOCKER** 若使用 core-surface coverage，package-wide coverage 也有交代
- [ ] `.coveragerc` omit 列表在 docs 有解释
- [ ] 不把 core-only coverage 写成 full-package coverage

### 4.2 CI
- [ ] Linux / macOS / Windows CI 通过
- [ ] 至少两个 Python 版本通过
- [ ] docs build 通过
- [ ] wheel build 通过
- [ ] public install smoke test 通过

### 4.3 correctness / stability
- [ ] native vs fallback agreement tests 存在
- [ ] schema regression tests 存在
- [ ] method catalog regression tests 存在
- [ ] representative wrapper smoke tests 存在

---

## 五、文档与用户路径

### 5.1 minimal user path
- [ ] **BLOCKER** 新用户 5 分钟内可完成 install + quickstart
- [ ] quickstart 中命令可直接运行
- [ ] API reference 与 quickstart 对象命名一致

### 5.2 methods pages
- [ ] 每个方法有 maturity status
- [ ] 每个方法有 assumptions / failure modes
- [ ] 明确哪些方法需要 optional dependencies
- [ ] 明确哪些方法为 wrapper / optional backend

### 5.3 reproducibility
- [ ] docs 中存在 reproducibility 页面
- [ ] CI / build / coverage / performance snapshot 路径清楚
- [ ] benchmark companion 与 software reproducibility 不混写

---

## 六、related software 对比完整性

### 6.1 必要对象
- [ ] **BLOCKER** PySDKit 被正面对比
- [ ] **BLOCKER** SSALib 被正面对比
- [ ] statsmodels 被正面对比
- [ ] PyEMD 被正面对比
- [ ] PyWavelets 被正面对比
- [ ] sktime / VMD continuation 被正面对比

### 6.2 对比维度
- [ ] 不是只做 scope-level 定性比较
- [ ] 有 workflow / API / machine-facing 维度
- [ ] 有 install / release / docs / CI 维度
- [ ] 有至少一项 empirical comparison
- [ ] 明确承认 specialist libraries 在家族深度上的优势

### 6.3 nearest competitor logic
- [ ] paper 中明确指出 PySDKit 是 nearest unified competitor
- [ ] De-Time 与 PySDKit 的差异不是“也统一接口”，而是更具体的软件对象差异

---

## 七、agent-friendly / machine-facing 一致性

### 7.1 machine contract
- [ ] schema assets 存在且可访问
- [ ] `list_catalog()` 输出稳定
- [ ] `recommend` 路径可运行
- [ ] `summary` / `meta` / `full` 输出模式清楚文档化
- [ ] artifact contract 与 docs 一致

### 7.2 MCP
- [ ] MCP server 入口真实可运行
- [ ] MCP 文档说明当前状态（local-first / remote-ready）
- [ ] 不夸大 registry / hosted status
- [ ] 工具名称与文档一致

### 7.3 token-aware claims
- [ ] **BLOCKER** 若宣称 low-token，必须有 benchmark 或定量表
- [ ] full / summary / meta payload 差异可解释
- [ ] 至少有一个 machine-facing demo workflow

### 7.4 agent evals
- [ ] 推荐至少有最小 agent eval harness
- [ ] 若没有，不要在 paper 中写过强的“agent-ready”表述

---

## 八、paper / submission consistency

### 8.1 abstract / intro
- [ ] **BLOCKER** 明确说明不是新 decomposition algorithm
- [ ] 主线是 workflow-oriented software layer
- [ ] 不把 benchmark / Dec-SR 结果当作 software paper 主贡献

### 8.2 related work
- [ ] 与 docs/comparisons 说法一致
- [ ] 没有回避最危险对手
- [ ] 不夸大自己对 specialist libraries 的替代性

### 8.3 claims
- [ ] **BLOCKER** 所有 public claims 均可在 repo/docs/release 复现
- [ ] 没有任何“upon acceptance we will release”与当前公开状态冲突
- [ ] adoption claim 与事实匹配
- [ ] coverage claim 与真实分母匹配

### 8.4 companion papers
- [ ] benchmark paper 与 software paper 边界明确
- [ ] Dec-SR paper 与 software paper 边界明确
- [ ] software paper 解释 why software contribution remains independent

---

## 九、cover letter consistency

### 9.1 必检项
- [ ] **BLOCKER** version to review 正确
- [ ] **BLOCKER** website 链接正确
- [ ] **BLOCKER** install path 正确
- [ ] **BLOCKER** active user community evidence 具体而非空泛
- [ ] CI / docs / release / tests 描述准确
- [ ] companion repo / companion paper 关系准确

### 9.2 不允许出现
- [ ] 没有与公开事实不符的 PyPI / release 表述
- [ ] 没有“extensive adoption”这类无依据表述
- [ ] 没有把 benchmark scientific claims 塞成 software novelty

---

## 十、最终 stop / go 规则

## GO（可以投）
只有在以下全部成立时才建议提交：

- [ ] install / release 事实完全一致
- [ ] public install reviewer 可复现
- [ ] PySDKit / SSALib 比较足够硬
- [ ] coverage 叙事诚实且有更广证据
- [ ] adoption evidence 至少有最基本具体性
- [ ] software paper 主线已回到 workflow + machine-facing abstraction
- [ ] benchmark / Dec-SR 已降为 companion utility evidence

## NO-GO（不建议投）
出现以下任一项即不建议提交：

- [ ] README/docs 写了不存在的公开安装路径
- [ ] paper 或 cover letter 对 package identity 仍然含混
- [ ] related software 仍然主要是定性和安全对手
- [ ] “low-token / agent-friendly” 只有口号没有证据
- [ ] coverage 数字仍可能被 reviewer 解读为误导
- [ ] benchmark artifact 与 installable software 边界仍然不清

---

## 十一、提交前最后 15 分钟检查

- [ ] README 首页是否一句话讲清“是什么 / 不是什么”
- [ ] 安装命令是否真实有效
- [ ] 版本号是否到处一致
- [ ] docs 导航是否干净
- [ ] comparisons 页面是否包含 PySDKit / SSALib
- [ ] release 页面是否与 docs 叙事一致
- [ ] cover letter 是否有 adoption evidence
- [ ] paper abstract 是否还在暗示 algorithmic novelty
- [ ] reviewer bundle 是否齐全

---

## 最后一条规则

**如果 reviewer 能在 5 分钟内通过公开页面复现一个明显事实错误，就不要投。**
