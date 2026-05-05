---
type: experiment
node_id: exp:openalex-002
title: "OpenAlex Search — LLM Industry OpenAlex Direct (Partial/Blocked)"
run_id: "20260427T072142Z-llm-industry-openalex-direct"
date: 2026-04-27T07:21:42Z
skill: openalex-search
status: partial_blocked
verdict: partial
freshness_window: "2025-04-27 to 2026-04-27"
---

# OpenAlex Search — LLM Industry OpenAlex Direct (Partial/Blocked)

**Run ID**: `20260427T072142Z-llm-industry-openalex-direct`
**Status**: ⚠️ Partial / Blocked

## Issue

ARIS created the query plan and the OpenAlex dry run completed, but ARIS did not complete the full export. Its bash tool treated OpenAlex commands as timed out, even though the dry-run output files later appeared.

## What Was Completed

- ✅ `openalex_queries.json` — 5 queries with title_and_abstract.search constraints
- ✅ `reviewer_direction.md` — Codex reviewer direction recorded
- ✅ `openalex/query_counts.csv` — dry-run counts
- ✅ `openalex/manifest.json` — dry-run manifest
- ❌ Full export — NOT RUN (blocked)

## Query Plan Summary

5 query families targeting high-precision industrial LLM/agent direction:

| Query Family | Reported Count | Diagnosis |
|---|---|---|
| `agentic_smart_manufacturing` | 23 | Good precision candidate |
| `llm_self_improving_industrial` | 259 | Good upper-bound candidate |
| `llm_predictive_prescriptive_maintenance` | 36 | Good precision candidate |
| `llm_kg_rag_industrial` | 30 | Good precision candidate |
| `trustworthy_industrial_llm` | 765 | Too broad; needs tightening |

## Shared Constraints

- `from_publication_date:2025-04-27`
- `to_publication_date:2026-04-27`
- `type:article`
- `language:en`
- `is_retracted:false`
- `is_paratext:false`

## Manual Commands Required

```bash
cd /Users/zhuyingqin/Documents/New\\ project/Auto-claude-code-research-in-sleep

# Step 1: dry-run
python3 crates/runtime/assets/skills/openalex-search/scripts/openalex_works_export.py \
  --queries lit-watch/runs/20260427T072142Z-llm-industry-openalex-direct/openalex_queries.json \
  --out lit-watch/runs/20260427T072142Z-llm-industry-openalex-direct/openalex \
  --dry-run

# Step 2: tighten trustworthy query, then full export:
python3 crates/runtime/assets/skills/openalex-search/scripts/openalex_works_export.py \
  --queries lit-watch/runs/20260427T072142Z-llm-industry-openalex-direct/openalex_queries.json \
  --out lit-watch/runs/20260427T072142Z-llm-industry-openalex-direct/openalex \
  --max-results 200
```

## Previous Run Context

Previous pass `20260427T070858Z-survey-of-large-language-model-applications-in-industry-including-self-evolution` produced 832 deduplicated works with useful records including manufacturing LLM agents, multi-agent prescriptive maintenance, 3D printing knowledge graphs, sensor failure reasoning, and GraphRAG for manufacturing.

## Reviewer Direction

Prioritized problem solved, industrial domain, agent capability, feedback/self-evolution mechanism, evidence type, evaluation, deployment risk, and human oversight.

## Output Files

- `openalex_queries.json` — Query plan
- `openalex/query_counts.csv` — Dry-run counts only
- `openalex/manifest.json` — Dry-run manifest
- `BLOCKED.md` — Blocker notice

## Connections

[AUTO-GENERATED from graph/edges.jsonl — do not edit manually]
