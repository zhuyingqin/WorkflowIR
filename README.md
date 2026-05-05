# WorkflowIR: Controlled Agent Workflows for Reliable Literature Search

[中文介绍](docs/workflowir-cn.md) | [Visual Guide](docs/workflowir_visual_learning.html)

WorkflowIR 是一个用于研究工具调用型 LLM Agent 可靠性的实验项目。当前第一阶段以论文检索为任务域，对比自由提示词 Agent 和带有 schema、precondition、effect、failure mode 的结构化 WorkflowIR Agent，观察真实调用中的超时、漏文件、宽泛检索、空结果、协议不合规和错误归因问题。

WorkflowIR studies one concrete question:

> Can an explicit workflow contract make tool-using LLM agents more reliable than a free-form prompt?

The first benchmark is **academic literature search**. A baseline agent is asked to search OpenAlex, design queries, export papers, and write a summary with minimal structure. WorkflowIR runs the same topic set through a typed workflow where each step has a schema, precondition, effect, failure mode, and trace record.

This repository is therefore not just a paper-search script. It is a dataset and evaluation scaffold for measuring whether workflow structure improves:

- task completion;
- protocol compliance;
- artifact quality and completeness;
- error attribution;
- recovery from broad, empty, missing, or failed tool calls.

## What This Project Does

The current reproducible comparison uses two run types: real free-form baseline runs and WorkflowIR-controlled runs. The offline controlled sandbox is kept as an optional first-layer artifact for later error-injection studies, but it is not required to reproduce the current WorkflowIR result.

**1. Real baseline agent traces**

A real ARIS/MiniMax/OpenAlex runner that asks an LLM agent to solve literature-search tasks. It saves the actual prompts, commands, stdout/stderr, query plans, OpenAlex outputs, summaries, blocked states, timeouts, and trace labels.

Output:

```text
lit-watch/real-agent-trials/
data/real_agent_litwatch_traces/workflowir_seed/
```

**2. WorkflowIR-controlled runs**

A controlled runner executes the same topics as a workflow graph:

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

The runner validates intermediate artifacts, repairs over-broad or zero-result queries, records node-level failures, and checks that every required output exists.

Output:

```text
lit-watch/workflowir-agent-runs/
data/workflowir_litsearch_eval/
```

**3. Optional controlled sandbox**

An offline literature-search sandbox with synthetic papers, declared tools, injected failures, and oracle labels. This layer is useful for controlled error attribution tests, but it is not part of the current real-run comparison.

Output:

```text
data/controlled_sandbox/litsearch_v1/
```

## How To Use

From the repository root:

```bash
cd /path/to/WorkflowIR
```

Run the WorkflowIR-controlled pipeline in plan-only mode:

```bash
python3 scripts/workflowir/run_workflowir_litsearch_trials.py \
  --config configs/workflowir_litsearch_trials.example.json \
  --max-trials 1
```

Run the WorkflowIR-controlled pipeline with real OpenAlex calls:

```bash
python3 scripts/workflowir/run_workflowir_litsearch_trials.py \
  --config configs/workflowir_litsearch_trials.example.json \
  --execute \
  --max-trials 1 \
  --max-results-per-query 50
```

Run real free-form baseline agent trials:

```bash
python3 scripts/workflowir/run_real_litwatch_trials.py \
  --config configs/real_litwatch_trials.example.json \
  --execute \
  --max-trials 5
```

The baseline command invokes ARIS and therefore needs a working ARIS binary plus the configured LLM API credentials. The WorkflowIR-controlled runner only needs Python and network access to OpenAlex when `--execute` is used.

Compare baseline and WorkflowIR batches:

```bash
python3 scripts/workflowir/analyze_workflowir_litsearch_effectiveness.py \
  --baseline-batch lit-watch/trial-batches/20260505T014639Z-workflowir-real-litwatch-seed/batch_manifest.json \
  --workflowir-batch lit-watch/workflowir-batches/20260505T052451Z-workflowir-controlled-litsearch-seed/batch_manifest.json \
  --out-dir data/workflowir_litsearch_eval
```

Optional: rebuild or validate the offline controlled sandbox for separate error-injection experiments:

```bash
python3 scripts/workflowir/build_controlled_litsearch_sandbox.py
python3 scripts/workflowir/build_controlled_litsearch_sandbox.py --validate-only
```

Open the visual explanation:

```text
docs/workflowir_visual_learning.html
```

GitHub Pages:

```text
https://zhuyingqin.github.io/WorkflowIR/
```

## Repository Layout

```text
configs/
  real_litwatch_trials.example.json          real baseline trial topics
  workflowir_litsearch_trials.example.json   controlled WorkflowIR trial topics

scripts/workflowir/
  build_controlled_litsearch_sandbox.py      offline controlled dataset builder
  run_real_litwatch_trials.py                free-form LLM-agent baseline runner
  build_real_litwatch_trace_dataset.py       trace miner for real agent runs
  run_workflowir_litsearch_trials.py         WorkflowIR-controlled runner
  analyze_workflowir_litsearch_effectiveness.py
                                               baseline-vs-WorkflowIR comparison
  build_paper_retrieval_db.py                utility for retrieval metadata

scripts/litwatch/
  aris_openalex_lit_watch.py                 ARIS + OpenAlex literature-watch executor
  run_aris_prompt.sh                         helper for direct ARIS prompt runs

scripts/datasets/
  build_aaai2026_awesome_index.py            auxiliary dataset utility
  build_llm_agents_tool_use_collection.py    auxiliary dataset utility
  download_aaai2026_ojs.py                   auxiliary dataset utility
  filter_aaai2026_llm_related.py             auxiliary dataset utility

openalex-search/
crates/runtime/assets/skills/openalex-search/
  reusable OpenAlex export skill and scripts

data/
  controlled_sandbox/                        generated controlled sandbox
  real_agent_litwatch_traces/                mined real-agent trace dataset
  workflowir_litsearch_eval/                 comparison reports

docs/
  workflowir-cn.md                            Chinese project introduction
  workflowir_visual_learning.html            GitHub Pages visual walkthrough
  upstream-aris-cn.md                        archived upstream ARIS Chinese README
  upstream-aris-en.md                        archived upstream ARIS English README
```

`idea-stage/` and `research-wiki/` are intentionally ignored and not tracked in Git.

## Current Seed Result

The seed comparison already shows why the controlled workflow matters:

```text
Baseline free-form agent:
  completion_rate = 0%
  timeout_rate    = 100%

WorkflowIR-controlled agent:
  completion_rate     = 100%
  timeout_rate        = 0%
  contract_pass_rate  = 100%
  full_export_rate    = 100%
```

This supports a reliability claim: WorkflowIR improves completion, artifact contracts, and error attribution for literature-search agents. It does not yet fully prove semantic retrieval quality. The next evaluation step is top-k paper relevance grading, either by humans or a separately prompted judge model.

## Upstream Foundation

WorkflowIR is built on top of ARIS-Code, a multi-agent research automation CLI. The original upstream README files were moved out of the repository root so the root README can describe this project directly:

- `docs/upstream-aris-cn.md`
- `docs/upstream-aris-en.md`

ARIS-Code provides the agent runtime, skill system, and literature-search infrastructure used by the real baseline runs.
