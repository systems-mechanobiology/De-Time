# De-Time：JMLR software track 最终核对清单（提交前 stop/go）
**用途**：投稿前最后一轮审查。  
**使用方法**：逐项填写 `YES / NO / N.A.` 与证据位置。任何 `STOP` 项为 `NO` 时，不要提交。  

---

## A. STOP 项（任何一项为 NO 就暂停提交）

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| A1. Public docs 中的安装命令在全新环境可成功执行 | YES | `docs/install.md` 现改为 GitHub 安装；2026-04-05 已在干净 venv 成功执行 `pip install "de-time @ git+https://github.com/systems-mechanobiology/De-Time.git@codex/jmlr-mloss-refactor"` 并跑通 `import detime` / CLI |
| A2. 若 docs 写 `pip install de-time`，对应发布页面确实存在且可安装 | N.A. | public docs 已不再把 `pip install de-time` 当当前安装命令；改为明确的 pre-release GitHub install story |
| A3. `detime` 已是 canonical implementation，而不是主要靠 shim 转发 | YES | `src/detime/` 下已有真实实现；`PUBLISHING.md` 已改为明确 `src/detime/` 是 canonical implementation |
| A4. `tsdecomp` 已明确降级为 legacy compatibility，而非双主身份 | YES | `src/tsdecomp/__init__.py` 和 docs/migration / docs/api / README 都把 `tsdecomp` 写成 deprecated compatibility alias |
| A5. public docs 首页与主导航不再显著展示 benchmark heatmaps / leaderboard walkthrough / agent tools | YES | `mkdocs.yml` 顶层 nav 已无这些页面；grep 审计中未再发现 `Agent Tools` / leaderboard walkthrough 出现在 public nav |
| A6. API 页面不再把 `run_leaderboard` / `merge_results` 等 benchmark-oriented 命令当一等 public interface | YES | `docs/api.md` 当前 public CLI 只列 `run` / `batch` / `profile` / `version` |
| A7. `submission/` 中不再有明显把 `tsdecomp` 当主名称的 reviewer-facing 文档 | YES | `submission/*.md` 中 `tsdecomp` 仅作为 deprecated legacy alias 出现，不再作为主身份 |
| A8. related software 已正面对上 PySDKit、SSALib、以及当前 `sktime` 的 VMD 现实 | YES | `docs/comparisons.md`、`submission/jmlr_mloss_software_paper_draft.md`、`submission/software_evidence.md` 已加入 `PySDKit` / `SSALib` / `sktime` |
| A9. paper 主线已经改成 software contribution，而非算法新颖性/方法清单 | YES | `submission/jmlr_mloss_software_paper_draft.md` 摘要、引言、软件概览都写成 workflow-oriented software contribution |
| A10. 发行包（wheel/sdist）中不再包含 benchmark artifact 主体代码或 agent-only 材料 | YES | 2026-04-05 已检查 `dist/*.tar.gz` 与 `dist/*.whl`；无 `synthetic_ts_bench` / `submission/` / `AGENT_*` / `JMLR_*` / `De-Time_*` |

---

## B. 包身份与安装一致性

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| B1. README、Quickstart、Install、PyPI/project metadata 说法一致 | YES | `README.md`、`docs/install.md`、`pyproject.toml` 统一为 `De-Time` / `de-time` / `detime`，且当前安装故事统一为 GitHub source install |
| B2. distribution 名与 import 名在文档中解释清楚 | YES | `README.md` 和 `docs/install.md` 明确写 product=`De-Time`、distribution=`de-time`、import=`detime` |
| B3. 已对 `de-time` / `detime` 潜在命名混淆作出明确决策 | YES | 当前决策是保留 `de-time` + `detime`，但 docs 明确禁止安装无关的 PyPI `detime` 项目，并在首个 PyPI release 前统一用 GitHub install |
| B4. `python -c "import detime"` 在干净环境成功 | YES | 2026-04-05 GitHub install、wheel smoke、sdist smoke 均已跑过 `import detime` |
| B5. `python -m detime --help` 在干净环境成功 | YES | 2026-04-05 GitHub install、wheel smoke 均已跑过 `python -m detime --help` |
| B6. 若保留 `tsdecomp`，其帮助与导入行为明确标记 legacy/deprecated | YES | `tests/legacy/test_tsdecomp_alias.py` 覆盖 import/CLI deprecation 行为；实际运行 `python -m tsdecomp version` 会发出 deprecation notice |
| B7. `python -m build` 与 `twine check dist/*` 均通过 | YES | 2026-04-05 本地验证通过 |

---

## C. 公开网站 / 文档站清洁度

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| C1. `mkdocs.yml` 顶层导航只保留软件核心页面 | YES | 当前 nav 为 Home / Why / Install / Quickstart / Choose a Method / Methods / API / Architecture / Tutorials / Comparisons / Migration / Reproducibility / Contributing / Citation |
| C2. 首页 hero/首屏只讲软件问题、软件贡献与边界 | YES | `docs/index.md` 首屏聚焦 workflow-oriented software、what it is / is not、package boundary |
| C3. Examples 首页以软件使用场景为主，而不是 leaderboard/benchmark 展示 | N.A. | public docs 已不再保留 `Examples` 首页；对应内容由 `Tutorials` 承担 |
| C4. Scenarios 页面不再把 benchmark-style comparisons 作为主要卖点 | N.A. | `Scenarios` 页面已从 public docs 移除 |
| C5. `Agent Tools` 已从 public nav 移除 | YES | grep 审计未再发现 `Agent Tools` 位于 docs 或 `mkdocs.yml` 的 public nav |
| C6. benchmark / artifact 页面已移到 internal/maintainer 附录或单独站点 | YES | public docs 已不再暴露 benchmark pages；基准工件转移到 companion repo `de-time-bench`，见 `docs/reproducibility.md` |
| C7. API 文档中的 public surface 已收缩到真正想支持的接口 | YES | `docs/api.md` 只保留 config/result/decompose/native helpers 与精简 CLI |
| C8. Methods Atlas 中对 native / built-in / wrapper / optional backend 的边界说明保留并清楚 | YES | `docs/methods.md` 仍保留 maturity labels 与 optional backend 边界说明 |

---

## D. 软件包内容边界

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| D1. `src/detime/` 为主实现路径 | YES | `src/detime/*.py` 与 `src/detime/methods/*.py` 为真实实现 |
| D2. `src/tsdecomp/` 主要只剩 compatibility wrappers | YES | `src/tsdecomp` 现主要做 re-export / warning / compatibility stubs |
| D3. `src/synthetic_ts_bench/` 未进入 installable package / sdist | YES | 目录已从主包删除；artifact 检查中 wheel/sdist 不含 `synthetic_ts_bench` |
| D4. `pyproject.toml` 已移除 `benchmarking` 之类会误导定位的 metadata | YES | `pyproject.toml` keywords 已无 `benchmarking` |
| D5. `MANIFEST.in` / build config 不再把 reviewer-only / agent-only 文件打进发行物 | YES | 2026-04-05 artifact 检查确认发行物中不含 `AGENT_*` / `JMLR_*` / `De-Time_*` |
| D6. 发行包中不含无关 submission 文档 | YES | 2026-04-05 wheel/sdist 均不含 `submission/` |

---

## E. 测试、CI、coverage、发布

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| E1. CI 主测试覆盖 Linux/macOS/Windows | YES | `.github/workflows/ci.yml` matrix 包含 `ubuntu-latest` / `macos-14` / `windows-latest`；PR 远端结果仍待 GitHub Actions 最终确认 |
| E2. CI 主测试覆盖至少两个 Python 版本 | YES | `.github/workflows/ci.yml` matrix 包含 Python `3.10` 与 `3.12` |
| E3. docs build 使用 strict 模式并通过 | YES | `mkdocs build --strict` 已于 2026-04-05 本地通过；workflow 也使用 strict 模式 |
| E4. wheels 构建和 smoke tests 通过 | YES | 本地 `python -m build --sdist --wheel`、wheel smoke、sdist smoke 已通过；wheels workflow 也已配置 smoke path |
| E5. 已设置 coverage fail-under 阈值 | YES | `.coveragerc` 现设 `fail_under = 90` |
| E6. 当前 coverage 数字可公开引用（badge、报告或 submission 文档） | YES | `docs/reproducibility.md` 与 `submission/software_evidence.md` 记录了当前 gated coverage `91.25%` |
| E7. 若 leaderboard/benchmark 命令仍公开存在，则已被充分测试 | N.A. | 这些命令已不在 public surface 中 |
| E8. 若 leaderboard/benchmark 命令未充分测试，则已从 public surface 移除 | YES | `docs/api.md` 和 CLI help 已不再公开这些命令 |

---

## F. Related software 与证据强度

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| F1. related software 中包含 statsmodels | YES | `docs/comparisons.md`、paper draft、`submission/software_evidence.md` |
| F2. related software 中包含 PyWavelets | YES | 同上 |
| F3. related software 中包含 PyEMD | YES | 同上 |
| F4. related software 中包含 PySDKit | YES | 同上 |
| F5. related software 中包含 SSALib | YES | 同上 |
| F6. VMD 相关讨论已更新到 `sktime` 维护现实，而不是只停留在 `vmdpy` | YES | `docs/comparisons.md`、paper draft、software evidence 均已改为 `sktime` 维护现实 |
| F7. 比较维度不只看方法表，还包含 workflow、result/config contract、CLI、multivariate、packaging、CI、coverage 等 | YES | `docs/comparisons.md` 现有 software-level axes 与 packaging/quality evidence 小节 |
| F8. 已提供至少一组最小软件层实证（例如 native vs fallback runtime） | YES | `docs/comparisons.md` 与 `submission/software_evidence.md` 记录了 `SSA` / `STD` / `STDR` 的 native vs python runtime snapshot |

---

## G. 论文与 cover letter

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| G1. 论文明确写明：这不是新算法 | YES | `submission/jmlr_mloss_software_paper_draft.md` 摘要与引言已明确写出 |
| G2. 论文明确写明：这不打算替代 specialized libraries | YES | paper 的 related software 与 limitations 小节已明确说明 |
| G3. 论文的主贡献定位是 unified workflow / config-result contract / reproducibility layer | YES | paper 的 Abstract / Public Software Surface / Introduction 已改成此主线 |
| G4. 论文单独说明了与 earlier benchmark artifact 的关系 | YES | paper 的 `Package Boundary and Relation to Earlier Artifacts` 小节单独说明了剥离关系 |
| G5. 论文单独说明了局限与非目标 | YES | paper 的 `Limitations and Non-Goals` 小节已加入 |
| G6. cover letter 主动解释了为什么这不是“artifact repackaging” | YES | `submission/cover_letter_jmlr_mloss.md` 明确解释 benchmark artifacts 已拆到 `de-time-bench` |
| G7. cover letter 提供了 release / CI / docs / coverage / user evidence | NO | release / CI / docs / coverage 已写，但可验证的独立 user evidence 仍然偏弱，仅有 early-adoption 的诚实表述 |
| G8. 若当前 adoption 仍早期，cover letter 已诚实表述而非夸大 | YES | cover letter 明确写当前 adoption 仍早期且不夸大 external community |

---

## H. Reviewer-facing grep / hygiene 审计

### H1. 关键 grep 检查
在提交前执行并记录结果：

```bash
grep -R "tsdecomp" submission docs README* -n
grep -R "run_leaderboard" docs README* -n
grep -R "merge_results" docs README* -n
grep -R "Agent Tools" docs mkdocs.yml -n
grep -R "benchmark" pyproject.toml README* docs -n
```

| 检查项 | YES/NO | 证据 / 备注 |
|---|---|---|
| H1. 所有 `tsdecomp` 出现都已被解释为 legacy compatibility | YES | 2026-04-05 grep 审计显示 public/submission 文档中的 `tsdecomp` 仅作为 deprecated alias 或 migration 语境出现 |
| H2. `run_leaderboard` 不再出现在 public-facing 主文档中（或其存在有充分理由） | YES | 2026-04-05 grep 审计未命中 public-facing docs/README/submission |
| H3. `merge_results` 不再出现在 public-facing 主文档中（或其存在有充分理由） | YES | 2026-04-05 grep 审计未命中 public-facing docs/README/submission |
| H4. `Agent Tools` 不再位于 public nav | YES | 2026-04-05 grep 审计未命中 docs 或 `mkdocs.yml` |
| H5. `benchmark` 不再作为 package 主定位关键词出现 | YES | `pyproject.toml` keywords 无 `benchmarking`；docs/README 中的 benchmark 只用于描述“已迁出/非主定位” |

---

## I. 可复现安装与运行 QA

在全新环境实际执行以下命令，并记录结果：

```bash
python -m venv .venv-jmlr-check
source .venv-jmlr-check/bin/activate  # Windows 用相应命令
pip install -U pip

# 使用 public docs 中写的真实安装命令
pip install de-time   # 或 Git/TestPyPI 安装命令

python -c "import detime; print(detime.__file__)"
python -m detime --help
python - <<'PY'
from detime import DecompositionConfig
print(DecompositionConfig)
PY
```

| 项目 | YES/NO | 证据 / 备注 |
|---|---|---|
| I1. 安装成功 | YES | 2026-04-05 在干净 venv 中成功执行 GitHub install 命令 |
| I2. `import detime` 成功 | YES | 同一干净 venv 中验证通过 |
| I3. CLI 成功 | YES | 同一干净 venv 中验证 `python -m detime --help` |
| I4. 基本 API 导入成功 | YES | 干净 venv 中验证 `from detime import DecompositionConfig, decompose` |
| I5. 文档中的最小示例能跑通 | YES | 干净 venv 中已跑最小 `SSA` 分解示例；wheel/sdist smoke 也跑通最小 `SSA` / `STD` decomposition |

---

## J. 最终签字页

### 当前结论（圈选）
- [ ] GO：可以提交
- [x] CONDITIONAL GO：小修后可提交
- [ ] NO-GO：仍不建议提交

### 最后仍可能被 mean reviewer 抓住的点
1. 首个正式 PyPI release 仍未完成，当前公开安装故事依赖 GitHub source install。
2. 外部 user evidence 仍然偏弱，cover letter 目前主要是诚实说明“adoption is early”。
3. GitHub Actions 远端 PR matrix 仍需在 PR 上最终跑绿。

### 负责人与日期
- 代码边界负责人：Codex / Zipeng Wu
- 文档站负责人：Codex / Zipeng Wu
- submission 材料负责人：Codex / Zipeng Wu
- 最终审核日期：2026-04-05

---

## K. 一句总原则
如果 reviewer 在 **GitHub 首页、docs 首页、API 页、安装页、submission checklist** 这五个地方看到的是**五个不同的软件故事**，那就不要投。  
只有当这五处都在说**同一个、边界清晰、可安装、可维护的软件故事**时，才值得提交。
