# Controlled Sandbox Literature Search v1

Dataset id: `controlled_sandbox_litsearch_v1`

This is the first-layer controlled sandbox for literature-search agents. It is
offline and synthetic by design: every paper, tool result, and injected fault can
be traced to an oracle record.

## Files

- `tools.json`: tool contracts. Every tool has schema, preconditions, effects,
  and failure modes.
- `corpus.jsonl`: synthetic scholarly corpus used by the sandbox.
- `tasks.jsonl`: task instances with prompts, allowed tools, expected traces,
  injections, and oracle labels.
- `attribution_taxonomy.json`: root-cause taxonomy and labels.
- `task_schema.json`: JSON Schema for task rows.
- `splits.json`: train/dev/test task ids.
- `evaluation_rubric.json`: first-layer metrics and baseline families.
- `manifest.json`: counts and design invariants.

## Current Scope

- Tools: 12
- Synthetic papers: 20
- Tasks: 30
- Injected tasks: 28
- Clean tasks: 2
- HTML first-layer status: complete

## Intended Evaluation

An agent should solve each `user_prompt` using only the declared tools and tool
observations. The evaluator can then score:

1. task success against `oracle.must_include_paper_ids` and
   `oracle.must_exclude_paper_ids`;
2. answer completeness against `oracle.required_answer_facets`;
3. fault attribution against `oracle.ground_truth_attribution_labels`;
4. recovery behavior against `injections[*].observable_symptoms` and
   `injections[*].recovery_hint`.

The first-layer HTML plan asks for 30-50 tasks and 10-20 tools. This generated
snapshot satisfies that target and keeps every task offline/reproducible.

## Rebuild Or Validate

```bash
python3 scripts/workflowir/build_controlled_litsearch_sandbox.py
python3 scripts/workflowir/build_controlled_litsearch_sandbox.py --validate-only
```
