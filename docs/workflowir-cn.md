# WorkflowIR 中文介绍

WorkflowIR 是一个用于研究 **工具调用型 LLM Agent 是否能通过结构化工作流变得更可靠** 的实验项目。

当前选择的任务域是 **论文检索**。原因很简单：论文检索看起来像一个普通 Agent 任务，但真实运行时很容易出现问题，比如检索式过宽、空结果、超时、漏写输出文件、没有保存中间证据、最终总结和检索结果不一致，或者无法判断错误到底来自提示词、工具、网络、数据源还是 Agent 自身决策。

WorkflowIR 的目标不是只做一个论文搜索脚本，而是构建一个可复现的数据集和评测框架，用来验证：

- Agent 是否能完成任务；
- Agent 是否遵守工具调用协议；
- 每一步是否产生了规定文件和可检查证据；
- 错误能否被定位到具体节点；
- 结构化 workflow 是否比自由提示词更稳定。

## 核心思想

普通自由提示词 Agent 的流程通常是：

```text
给 Agent 一个主题
  -> Agent 自己决定怎么搜
  -> Agent 自己调用工具
  -> Agent 自己判断是否完成
```

这种方式灵活，但不容易控制和归因。一旦失败，我们很难判断是检索式设计错了、OpenAlex 调用失败了、结果太宽泛、输出文件缺失，还是 Agent 根本没有按照任务协议执行。

WorkflowIR 把同一个任务拆成显式节点：

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

每个节点都有四类约束：

- `schema`：输入和输出必须是什么格式；
- `precondition`：运行前必须满足什么条件；
- `effect`：运行后必须产生什么文件、状态或证据；
- `failure mode`：失败时应该归因到哪类错误。

这样做的意义是：LLM 可以参与规划和判断，但 workflow runner 负责检查协议、保存中间产物、修复明显错误、记录 trace，并在失败时给出可解释的错误位置。

## 当前实验到底跑什么

目前用于说明 WorkflowIR 有效性的，是两组真实运行对比：一组是自由提示词 baseline，一组是 WorkflowIR 结构化 workflow 版本。

**第一组：真实自由 Agent Runs**

调用真实 ARIS/MiniMax/OpenAlex 运行论文检索任务，收集真实 Agent 调用过程中产生的错误和异常。这一层不是人工编造错误，而是保留实际运行时的 prompt、命令、stdout/stderr、查询计划、OpenAlex 结果、SUMMARY、BLOCKED 状态和 timeout 信息。

主要输出：

```text
lit-watch/real-agent-trials/
data/real_agent_litwatch_traces/workflowir_seed/
```

**第二组：WorkflowIR Agent Runs**

对相同主题使用结构化 workflow 执行。Runner 会先检查 query plan，再做 OpenAlex dry-run，发现过宽或空结果后进行修复，然后执行完整导出，最后检查所有必需文件和质量记录。

主要输出：

```text
lit-watch/workflowir-agent-runs/
data/workflowir_litsearch_eval/
```

## 数据集保存什么

这个项目生成和保存的不只是最终答案，而是完整的 Agent 运行证据：

- 任务主题和配置；
- prompt contract；
- 工具 schema、precondition、effect、failure mode；
- Agent 或 workflow 生成的 query plan；
- OpenAlex dry-run counts；
- OpenAlex full export metadata；
- 每个节点的状态和失败模式；
- stdout/stderr；
- `SUMMARY.md`、`QUALITY_NOTES.md`、`RETRIEVAL_EVAL.json`；
- baseline 与 WorkflowIR 的对比报告。

这些信息后续可以用于训练或评估：哪些错误真实发生、错误发生在哪个节点、Agent 是否恢复、WorkflowIR 是否提升完成率和可归因性。

## 如何运行

先进入仓库根目录：

```bash
cd /path/to/WorkflowIR
```

只生成 WorkflowIR 计划，不调用 OpenAlex：

```bash
python3 scripts/workflowir/run_workflowir_litsearch_trials.py \
  --config configs/workflowir_litsearch_trials.example.json \
  --max-trials 1
```

运行 WorkflowIR 版本并真实调用 OpenAlex：

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

注意：baseline 会调用 ARIS 和 LLM API，因此需要本地 ARIS binary 和对应 API key。WorkflowIR runner 在 `--execute` 时只需要能访问 OpenAlex；不加 `--execute` 时只是 plan-only。

对比 baseline 和 WorkflowIR：

```bash
python3 scripts/workflowir/analyze_workflowir_litsearch_effectiveness.py \
  --baseline-batch lit-watch/trial-batches/20260505T014639Z-workflowir-real-litwatch-seed/batch_manifest.json \
  --workflowir-batch lit-watch/workflowir-batches/20260505T052451Z-workflowir-workflow-litsearch-seed/batch_manifest.json \
  --out-dir data/workflowir_litsearch_eval
```

## 当前种子结果

已有 seed run 显示：

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

这说明当前实验已经能支持一个初步结论：WorkflowIR 可以提升论文检索 Agent 的执行可靠性、协议遵守程度和错误归因能力。

但它还没有完全证明“检索到的论文语义质量一定更高”。下一步需要加入 top-k 论文相关性评估，可以由人工标注，也可以使用单独的 LLM judge 对检索结果进行质量打分。

## 目录结构

```text
configs/                         实验配置和 prompt contract
scripts/workflowir/              WorkflowIR 实验、trace 构建和对比分析
scripts/litwatch/                ARIS + OpenAlex 真实 Agent runner
scripts/datasets/                辅助数据集脚本
data/real_agent_litwatch_traces/ 真实 Agent trace 数据集
data/workflowir_litsearch_eval/  有效性对比报告
docs/                            中文说明、可视化页面和上游 ARIS 归档文档
```

`idea-stage/` 和 `research-wiki/` 是本地工作目录，已被 `.gitignore` 屏蔽，不会上传到 GitHub。
