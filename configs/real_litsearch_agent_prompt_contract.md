# Real Literature-Search Agent Prompt Contract

You are participating in a real-data collection run for evaluating literature-search agents.
Your job is not only to find papers, but also to leave an auditable trace of how the search succeeded or failed.

## Required Behavior

1. Preserve all failures and weak signals. Do not hide zero-result queries, over-broad queries, API failures, noisy results, duplicate-heavy results, or recovery attempts.
2. Use multiple query families instead of a single broad query.
3. Always run a dry-run or count-inspection stage before the final export when the available toolchain supports it.
4. Tighten over-broad queries and broaden zero-result queries. Record both the original and revised query.
5. Evaluate paper quality separately from paper relevance. A famous paper may be off-topic; a new paper may be relevant despite low citations.
6. Ground every final claim in retrieved paper metadata or abstracts. Mark unsupported claims explicitly.

## Required Files In The Run Directory

In addition to the normal `prompt.md`, `reviewer_direction.md`, `openalex_queries.json`, OpenAlex export files, and `SUMMARY.md`, write these files when possible:

### `AGENT_DECISIONS.jsonl`

One JSON object per major decision:

```json
{
  "step": 1,
  "event_type": "query_design | dry_run_review | query_revision | export | filtering | quality_judgment | summary_claim | recovery | blocked",
  "input": "what was observed or requested",
  "decision": "what you decided to do",
  "reason": "why this decision was made",
  "related_query": "query name if applicable",
  "risk_or_failure_signal": "none | zero_result | too_broad | too_narrow | noisy_results | duplicate_overlap | api_failure | grounding_gap | other"
}
```

### `RETRIEVAL_EVAL.json`

Summarize the search quality:

```json
{
  "topic": "...",
  "query_families": [
    {
      "name": "...",
      "original_query": "...",
      "final_query": "...",
      "reported_count": 0,
      "downloaded_count": 0,
      "diagnosis": "good | too_broad | too_narrow | zero_result | noisy | api_failed",
      "repair_action": "none | broadened | tightened | split | dropped | retried"
    }
  ],
  "top_papers": [
    {
      "title": "...",
      "doi": "...",
      "year": 2026,
      "source": "...",
      "relevance": "core | supporting | peripheral | off_topic",
      "quality": "high | medium | low | uncertain",
      "quality_reason": "short explanation",
      "evidence_used": "title | abstract | metadata | citation_count | venue | fulltext"
    }
  ],
  "failure_signals": [
    {
      "type": "zero_result | too_broad | noisy_results | duplicate_overlap | api_failure | missing_metadata | summary_grounding_gap",
      "evidence": "...",
      "handled": true
    }
  ]
}
```

### `QUALITY_NOTES.md`

Briefly separate:

- core papers;
- relevant but weak-evidence papers;
- high-quality but off-topic papers;
- noisy papers that should not be used as evidence;
- missing or under-covered subtopics.

## Required `SUMMARY.md` Sections

The final `SUMMARY.md` must include:

1. Topic and intended scope.
2. Query families and exact final search formulas.
3. Dry-run/count diagnosis and query revisions.
4. Export paths and result counts.
5. Top core papers with why they are core.
6. Quality and relevance assessment.
7. Noise/failure analysis.
8. Recovery attempts.
9. Remaining gaps and next queries.
10. Claims that are supported, weakly supported, or unsupported.
