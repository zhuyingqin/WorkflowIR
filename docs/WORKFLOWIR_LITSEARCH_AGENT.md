# WorkflowIR-Controlled LitSearch Agent

This is the controlled counterpart to the free-form ARIS literature-search runs.
The goal is to test whether explicit workflow control improves agent reliability.

## Baseline

The baseline agent owns the whole task:

```text
prompt -> plan queries -> call OpenAlex -> inspect counts -> export -> summarize -> update wiki -> exit
```

The first real batch showed the main weakness:

```text
5/5 timeout
4/5 missing summary
multiple broad queries
partial protocol compliance
```

## WorkflowIR Version

The WorkflowIR runner decomposes the same task into explicit nodes:

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

Each node has:

- schema-like preconditions;
- explicit effects;
- known failure modes;
- a JSONL trace row;
- deterministic recovery where possible.

The LLM/agent is no longer trusted to remember the whole protocol. The runner
forces the protocol:

- query count must be 2-5;
- dry-run/count inspection must happen before full export;
- broad queries are tightened;
- zero-result queries are broadened;
- `SUMMARY.md`, `RETRIEVAL_EVAL.json`, `QUALITY_NOTES.md`, and
  `AGENT_DECISIONS.jsonl` are written by the runner;
- missing artifacts fail the contract.

## Run

Plan only:

```bash
python3 scripts/run_workflowir_litsearch_trials.py \
  --config configs/workflowir_litsearch_trials.example.json
```

Execute real OpenAlex retrieval:

```bash
python3 scripts/run_workflowir_litsearch_trials.py \
  --config configs/workflowir_litsearch_trials.example.json \
  --execute
```

Compare against the baseline batch:

```bash
python3 scripts/analyze_workflowir_litsearch_effectiveness.py \
  --baseline-batch lit-watch/trial-batches/20260505T014639Z-workflowir-real-litwatch-seed/batch_manifest.json \
  --workflowir-batch <workflowir-batch>/batch_manifest.json
```

## Evidence Claim

WorkflowIR is effective if, on the same topic set, it improves:

- completion rate;
- timeout rate;
- required artifact contract pass rate;
- full export rate;
- broad-query and zero-result recovery;
- error attribution quality.
