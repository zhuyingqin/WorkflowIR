# Paper Retrieval Database

This SQLite database stores papers retrieved by real lit-watch/OpenAlex runs and
adds explainable quality signals.

Database: `data/paper_retrieval_db/papers.sqlite`

## What Counts As Paper Quality?

Quality is multi-dimensional:

- `integrity_score`: not retracted, not paratext, English article metadata.
- `source_score`: DOI/source/core venue/source type signals.
- `evidence_score`: title, abstract length, reference count, OA availability.
- `impact_score`: citation count and age-normalized citation velocity.
- `recency_score`: recent papers get a small boost.
- `relevance_score`: run-specific title/abstract/query overlap and matched query count.

The global `quality_score` is only a bootstrap ranking signal:

`0.28 integrity + 0.22 source + 0.22 evidence + 0.18 impact + 0.10 recency`

For each run, use `ranked_run_papers.retrieval_quality_score`:

`0.55 run relevance + 0.45 global quality`

## Tables

- `papers`: normalized OpenAlex metadata plus raw JSON.
- `runs`: retrieval run metadata and query terms.
- `paper_runs`: many-to-many provenance linking papers to runs.
- `quality_scores`: global paper quality sub-scores.
- `run_relevance_scores`: query/run-specific relevance sub-scores.
- `quality_flags`: weak warning flags such as missing DOI, short abstract, non-core source.
- `ranked_papers`: view sorted by global quality.
- `ranked_run_papers`: view sorted by run-specific retrieval quality.

## Example Queries

```sql
SELECT title, publication_year, source_name, quality_score
FROM ranked_papers
LIMIT 20;

SELECT title, retrieval_quality_score, relevance_score, quality_score
FROM ranked_run_papers
WHERE run_id = '20260427T214457Z-industrial-llm-agent-workflow-orchestration'
LIMIT 20;
```
