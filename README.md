# WorkflowIR: 用结构化 Workflow 提升文献检索 Agent 可靠性

[English README](README_EN.md) | [中文介绍](docs/workflowir-cn.md) | [可视化学习页](docs/workflowir_visual_learning.html)

WorkflowIR 是一个用于研究 **工具调用型 LLM Agent 是否能通过结构化工作流变得更可靠** 的实验项目。当前任务域是论文检索：我们对比自由提示词 Agent 和带有 `schema`、`precondition`、`effect`、`failure mode` 的 WorkflowIR 结构化 workflow，观察真实调用中的超时、漏文件、宽泛检索、空结果、协议不合规和错误归因问题。

这个项目想回答一个具体问题：

> 显式的 WorkflowIR contract，能否让工具调用型 LLM Agent 比自由提示词更稳定、更可检查、更容易定位错误？

论文检索是一个很适合测试这个问题的任务。普通 Agent 看起来只是在搜索 OpenAlex、设计 query、导出论文、写 summary，但真实运行中经常出现：query 太宽、query 为空、导出失败、结果文件缺失、summary 和检索结果不一致、超时后无法判断错误来源等问题。WorkflowIR 把同一个任务拆成带类型和约束的节点，让每一步都留下可审计证据。

本仓库不只是一个 paper-search 脚本，而是一个用于评估结构化 workflow 是否能提升 Agent 可靠性的实验框架。当前重点衡量：

- 任务完成率；
- 工具调用协议遵守程度；
- 输出文件和中间证据是否完整；
- 错误能否定位到具体节点；
- 对宽泛、空结果、漏文件、失败工具调用的恢复能力；
- 同一主题下 Workflow 和 WorkflowIR 的检索质量差异。

![WorkflowIR experiment results](docs/workflowir_experiment_results.png)

![Workflow vs WorkflowIR search-quality experiment](docs/workflow_vs_workflowir_search_quality_experiment.png)

最新的 paired-topic 实验在同一文献检索主题上对比自由 Workflow 和 WorkflowIR，并用同一个检索质量评估器打分。报告包含候选池规模、top-k 相关性、核心论文比例、anchor 覆盖、质量信号和审计产物：

- [搜索质量对比报告](data/workflowir_litsearch_eval/workflow_vs_workflowir_search_quality_workflow_planning_benchmarks.md)
- [机器可读 JSON 结果](data/workflowir_litsearch_eval/workflow_vs_workflowir_search_quality_workflow_planning_benchmarks.json)

## 项目做什么

当前可复现实验包含两类运行：真实自由 Agent baseline 和 WorkflowIR 结构化 workflow。

**1. 真实自由 Agent traces**

这一组使用真实 ARIS/MiniMax/OpenAlex runner，让 LLM Agent 自由完成论文检索任务。系统保存真实 prompt、命令、stdout/stderr、query plan、OpenAlex 输出、summary、blocked 状态、timeout 和自动挖掘的异常标签。

输出目录：

```text
lit-watch/real-agent-trials/
data/real_agent_litwatch_traces/workflowir_seed/
```

**2. WorkflowIR workflow runs**

这一组把相同主题转成显式 workflow 图执行：

```text
create_run
  -> plan_queries
  -> validate_query_plan
  -> dry_run_counts
  -> repair_queries
  -> full_export
  -> evaluate_results
  -> verify_contract
```

Runner 会检查中间产物、修复过宽或零结果 query、记录节点级失败，并验证所有必需输出文件是否存在。

输出目录：

```text
lit-watch/workflowir-agent-runs/
data/workflowir_litsearch_eval/
```

## 如何运行

进入仓库根目录：

```bash
cd /path/to/WorkflowIR
```

只生成 WorkflowIR plan，不调用 OpenAlex：

```bash
python3 scripts/workflowir/run_workflowir_litsearch_trials.py \
  --config configs/workflowir_litsearch_trials.example.json \
  --max-trials 1
```

运行 WorkflowIR，并真实调用 OpenAlex：

```bash
python3 scripts/workflowir/run_workflowir_litsearch_trials.py \
  --config configs/workflowir_litsearch_trials.example.json \
  --execute \
  --max-trials 1 \
  --max-results-per-query 50
```

运行真实自由 Agent baseline：

```bash
python3 scripts/workflowir/run_real_litwatch_trials.py \
  --config configs/real_litwatch_trials.example.json \
  --execute \
  --max-trials 5
```

baseline 会调用 ARIS 和 LLM API，因此需要可用的 ARIS binary 和对应 API 凭证。WorkflowIR runner 在 `--execute` 时只需要 Python 和访问 OpenAlex 的网络环境。

对比 baseline 和 WorkflowIR batch：

```bash
python3 scripts/workflowir/analyze_workflowir_litsearch_effectiveness.py \
  --baseline-batch lit-watch/trial-batches/20260505T014639Z-workflowir-real-litwatch-seed/batch_manifest.json \
  --workflowir-batch lit-watch/workflowir-batches/20260505T052451Z-workflowir-workflow-litsearch-seed/batch_manifest.json \
  --out-dir data/workflowir_litsearch_eval
```

对比同一主题下 Workflow 和 WorkflowIR 的搜索质量：

```bash
python3 scripts/workflowir/evaluate_workflow_vs_workflowir_search_quality.py \
  --workflow-run-dir lit-watch/real-agent-trials/20260505T020439Z-benchmarks-for-tool-using-llm-agents-that-evaluate-dag-planning-executable-workf \
  --workflowir-run-dir lit-watch/workflowir-agent-runs/20260505T052505Z-benchmarks-for-tool-using-llm-agents-that-evaluate-dag-planning-executable-workflows-api-tool-se \
  --output-prefix workflow_vs_workflowir_search_quality_workflow_planning_benchmarks
```

打开可视化说明：

```text
docs/workflowir_visual_learning.html
```

GitHub Pages：

```text
https://zhuyingqin.github.io/WorkflowIR/
```

## 目录结构

```text
configs/
  real_litwatch_trials.example.json          真实 baseline 主题配置
  workflowir_litsearch_trials.example.json   WorkflowIR workflow 主题配置

scripts/workflowir/
  run_real_litwatch_trials.py                自由 LLM Agent baseline runner
  build_real_litwatch_trace_dataset.py       真实 Agent trace 挖掘脚本
  run_workflowir_litsearch_trials.py         WorkflowIR workflow runner
  analyze_workflowir_litsearch_effectiveness.py
                                             baseline-vs-WorkflowIR 完成率对比
  evaluate_workflow_vs_workflowir_search_quality.py
                                             Workflow-vs-WorkflowIR 搜索质量对比
  build_paper_retrieval_db.py                检索元数据工具

scripts/litwatch/
  aris_openalex_lit_watch.py                 ARIS + OpenAlex 文献检索执行器
  run_aris_prompt.sh                         直接运行 ARIS prompt 的 helper

scripts/datasets/
  build_aaai2026_awesome_index.py            辅助数据集工具
  build_llm_agents_tool_use_collection.py    辅助数据集工具
  download_aaai2026_ojs.py                   辅助数据集工具
  filter_aaai2026_llm_related.py             辅助数据集工具

openalex-search/
crates/runtime/assets/skills/openalex-search/
  可复用 OpenAlex 导出 skill 和脚本

data/
  real_agent_litwatch_traces/                真实 Agent trace 数据集
  workflowir_litsearch_eval/                 对比报告和评估结果

docs/
  workflowir-cn.md                           中文项目介绍
  workflowir_visual_learning.html            GitHub Pages 可视化学习页
  upstream-aris-cn.md                        上游 ARIS 中文 README 归档
  upstream-aris-en.md                        上游 ARIS 英文 README 归档
```

`idea-stage/` 和 `research-wiki/` 是本地工作目录，已被 `.gitignore` 屏蔽，不会上传到 GitHub。

## 当前种子结果

已有 seed comparison 显示结构化 workflow 的价值：

```text
Baseline free-form agent:
  completion_rate = 0%
  timeout_rate    = 100%

WorkflowIR workflow agent:
  completion_rate     = 100%
  timeout_rate        = 0%
  contract_pass_rate  = 100%
  full_export_rate    = 100%
```

这支持一个可靠性结论：WorkflowIR 能提升文献检索 Agent 的完成率、artifact contract 遵守程度和错误归因能力。

搜索质量实验进一步说明：WorkflowIR 不一定最大化候选池规模，但能生成更强的审计链，并在当前 paired-topic 结果中取得更高的 top-k 相关性和综合检索质量分数。自由 Workflow 的候选池更大，适合追求 recall，但也带来更高筛选成本。

## 上游基础

WorkflowIR 构建在 ARIS-Code 之上。ARIS-Code 提供多 Agent 研究自动化 CLI、skill 系统和文献检索基础设施。为了让根目录 README 专门介绍本项目，原始上游 README 已归档到：

- `docs/upstream-aris-cn.md`
- `docs/upstream-aris-en.md`
