# Real Agent Literature-Search Data Protocol

This protocol defines how to generate comparable real-data runs for evaluating literature-search agents.

## Goal

For each topic, the agent should perform a real literature-search workflow, call real tools/APIs, preserve failures, and save enough artifacts for later evaluation.

The dataset should answer:

- Did the agent generate good search queries?
- Did it retrieve relevant and high-quality papers?
- Did it detect and repair bad queries or noisy results?
- Did the final summary stay grounded in retrieved evidence?
- Did the agent leave enough trace information for error attribution?

## Minimal Loop

1. Choose one topic.
2. Run the same prompt contract for every method/model.
3. Let the agent create query families.
4. Run count inspection or dry-run.
5. Let the agent revise bad queries.
6. Export results.
7. Build the paper retrieval database.
8. Score relevance, quality, noise, and recovery.
9. Compare methods on the same topics.

## Unified Prompt Contract

The shared prompt contract is stored at:

`configs/real_litsearch_agent_prompt_contract.md`

It requires every real run to save:

- `openalex_queries.json`
- OpenAlex export files
- `SUMMARY.md`
- `AGENT_DECISIONS.jsonl`
- `RETRIEVAL_EVAL.json`
- `QUALITY_NOTES.md`

The trial runner appends this contract to every agent run through `--extra-instruction`.

## What To Save

### Run Metadata

- topic
- model
- timestamp
- prompt
- allowed tools
- output directory
- API/tool settings

Saved by:

- `prompt.md`
- `watch_manifest.json`
- batch `batch_manifest.json`

### Query Planning

- query families
- exact query strings
- filters
- original and revised queries
- rationale for query design

Saved by:

- `openalex_queries.json`
- `AGENT_DECISIONS.jsonl`
- `SUMMARY.md`

### Tool/API Execution

- dry-run counts
- final downloaded counts
- deduplicated counts
- per-query reported/downloaded results
- API failures or blocked runs

Saved by:

- `openalex/manifest.json`
- `openalex/query_counts.csv` if produced
- `BLOCKED.md`
- `AGENT_DECISIONS.jsonl`

### Retrieved Papers

- OpenAlex id
- DOI
- title
- year
- venue/source
- abstract
- citation count
- topics
- matched query family

Saved by:

- `openalex/all_results_deduped.jsonl`
- `data/paper_retrieval_db/papers.sqlite`

### Quality And Relevance Judgments

- relevance: core / supporting / peripheral / off-topic
- quality: high / medium / low / uncertain
- quality reason
- evidence source
- noise flags

Saved by:

- `RETRIEVAL_EVAL.json`
- `QUALITY_NOTES.md`
- `quality_scores`
- `run_relevance_scores`
- `quality_flags`

### Final Summary Grounding

- top papers used as evidence
- claims supported by retrieved papers
- weakly supported claims
- unsupported claims
- remaining gaps

Saved by:

- `SUMMARY.md`
- `RETRIEVAL_EVAL.json`

## First Evaluation Metrics

Use these before building a complex learned judge:

- `Precision@K`: fraction of top K papers judged core/supporting.
- `Noise@K`: fraction of top K judged peripheral/off-topic.
- `Query Failure Rate`: zero-result or too-broad query families.
- `Repair Rate`: bad query families that were fixed before export.
- `Duplicate Ratio`: deduped works divided by downloaded rows.
- `Grounded Claim Rate`: final claims supported by retrieved papers.
- `Quality@K`: average `quality_score` among top K relevant papers.

## Current Scripts

Plan or run real trials:

```bash
python3 scripts/run_real_litwatch_trials.py \
  --config configs/real_litwatch_trials.example.json

python3 scripts/run_real_litwatch_trials.py \
  --config configs/real_litwatch_trials.example.json \
  --execute
```

Build trace dataset from run artifacts:

```bash
python3 scripts/build_real_litwatch_trace_dataset.py \
  --runs-dir lit-watch/real-agent-trials \
  --out-dir data/real_agent_litwatch_traces/workflowir_seed
```

Build paper retrieval database:

```bash
python3 scripts/build_paper_retrieval_db.py \
  --runs-dir lit-watch/real-agent-trials \
  --out-dir data/paper_retrieval_db/workflowir_seed
```

## Important Separation

The controlled sandbox is useful for testing evaluator mechanics.

The real trial runner is what generates evidence for agent effectiveness.
