#!/usr/bin/env python3
"""Build a SQLite paper retrieval database with explainable quality signals.

The database is built from existing lit-watch OpenAlex exports. It keeps raw
metadata, run-level retrieval provenance, quality sub-scores, task relevance
scores, and flags that explain why a paper may be weak evidence.
"""

from __future__ import annotations

import argparse
import json
import math
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


DEFAULT_RUNS_DIR = "lit-watch/runs"
DEFAULT_OUT_DIR = "data/paper_retrieval_db"
DEFAULT_DB_NAME = "papers.sqlite"
CURRENT_YEAR = 2026

STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "into",
    "is",
    "it",
    "large",
    "language",
    "model",
    "models",
    "of",
    "on",
    "or",
    "the",
    "to",
    "using",
    "via",
    "with",
}


def tokenize(text: str) -> set[str]:
    tokens = re.findall(r"[a-zA-Z][a-zA-Z0-9_-]{2,}", text.lower())
    return {token for token in tokens if token not in STOPWORDS}


def clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, UnicodeDecodeError):
        return None


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    try:
        with path.open(encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    rows.append(json.loads(line))
    except FileNotFoundError:
        return []
    return rows


def discover_exports(runs_dir: Path) -> list[tuple[Path, Path]]:
    exports: list[tuple[Path, Path]] = []
    for results_path in sorted(runs_dir.glob("*/openalex/all_results_deduped.jsonl")):
        run_dir = results_path.parents[1]
        exports.append((run_dir, results_path))
    return exports


def source_info(work: dict[str, Any]) -> dict[str, Any]:
    location = work.get("primary_location")
    source = {}
    if isinstance(location, dict) and isinstance(location.get("source"), dict):
        source = location["source"]
    return {
        "source_name": source.get("display_name") or (location or {}).get("raw_source_name") if isinstance(location, dict) else None,
        "source_type": source.get("type"),
        "source_is_core": bool(source.get("is_core")) if source else False,
        "source_is_oa": bool(source.get("is_oa")) if source else False,
        "source_is_in_doaj": bool(source.get("is_in_doaj")) if source else False,
        "host_organization_name": source.get("host_organization_name"),
    }


def primary_topic(work: dict[str, Any]) -> dict[str, Any]:
    topic = work.get("primary_topic")
    if not isinstance(topic, dict):
        return {"primary_topic": None, "primary_field": None, "primary_subfield": None}
    field = topic.get("field") if isinstance(topic.get("field"), dict) else {}
    subfield = topic.get("subfield") if isinstance(topic.get("subfield"), dict) else {}
    return {
        "primary_topic": topic.get("display_name"),
        "primary_field": field.get("display_name"),
        "primary_subfield": subfield.get("display_name"),
    }


def paper_id(row: dict[str, Any]) -> str | None:
    work = row.get("work") if isinstance(row.get("work"), dict) else {}
    ids = work.get("ids") if isinstance(work.get("ids"), dict) else {}
    return row.get("openalex_id") or ids.get("openalex") or work.get("id")


def abstract_text(row: dict[str, Any]) -> str:
    abstract = row.get("abstract")
    if isinstance(abstract, str) and abstract.strip():
        return abstract.strip()
    work = row.get("work") if isinstance(row.get("work"), dict) else {}
    inverted = work.get("abstract_inverted_index")
    if not isinstance(inverted, dict):
        return ""
    positions: list[tuple[int, str]] = []
    for token, indexes in inverted.items():
        if isinstance(indexes, list):
            positions.extend((int(index), token) for index in indexes if isinstance(index, int))
    return " ".join(token for _, token in sorted(positions))


def normalize_paper(row: dict[str, Any]) -> dict[str, Any] | None:
    work = row.get("work") if isinstance(row.get("work"), dict) else {}
    openalex_id = paper_id(row)
    if not openalex_id:
        return None
    info = source_info(work)
    topic = primary_topic(work)
    open_access = work.get("open_access") if isinstance(work.get("open_access"), dict) else {}
    doi = row.get("doi") or (work.get("ids") or {}).get("doi") if isinstance(work.get("ids"), dict) else None
    title = row.get("title") or work.get("display_name") or work.get("title") or ""
    abstract = abstract_text(row)
    return {
        "openalex_id": openalex_id,
        "doi": doi,
        "title": title,
        "abstract": abstract,
        "publication_year": work.get("publication_year"),
        "publication_date": work.get("publication_date"),
        "type": work.get("type"),
        "language": work.get("language"),
        "cited_by_count": work.get("cited_by_count") or 0,
        "referenced_works_count": work.get("referenced_works_count") or 0,
        "is_retracted": bool(work.get("is_retracted")),
        "is_paratext": bool(work.get("is_paratext")),
        "is_oa": bool(open_access.get("is_oa")),
        "oa_status": open_access.get("oa_status"),
        "matched_queries": row.get("matched_queries") if isinstance(row.get("matched_queries"), list) else [],
        "raw_json": json.dumps(row, ensure_ascii=False),
        **info,
        **topic,
    }


def quality_scores(paper: dict[str, Any]) -> dict[str, float]:
    year = paper.get("publication_year")
    try:
        age = max(1, CURRENT_YEAR - int(year) + 1)
    except (TypeError, ValueError):
        age = 4
    citations = int(paper.get("cited_by_count") or 0)
    references = int(paper.get("referenced_works_count") or 0)
    abstract_len = len(paper.get("abstract") or "")

    integrity = 1.0
    if paper.get("is_retracted"):
        integrity -= 0.75
    if paper.get("is_paratext"):
        integrity -= 0.35
    if paper.get("language") and paper.get("language") != "en":
        integrity -= 0.2
    if paper.get("type") and paper.get("type") != "article":
        integrity -= 0.15
    integrity = clamp(integrity)

    source = 0.35
    if paper.get("source_name"):
        source += 0.2
    if paper.get("source_is_core"):
        source += 0.25
    if paper.get("source_type") in {"journal", "conference"}:
        source += 0.1
    if paper.get("doi"):
        source += 0.1
    source = clamp(source)

    evidence = 0.0
    if paper.get("title"):
        evidence += 0.15
    if paper.get("doi"):
        evidence += 0.1
    evidence += clamp(abstract_len / 1200.0) * 0.45
    evidence += clamp(references / 40.0) * 0.2
    if paper.get("is_oa"):
        evidence += 0.1
    evidence = clamp(evidence)

    citation_velocity = citations / age
    impact = 0.6 * clamp(math.log1p(citations) / math.log1p(100)) + 0.4 * clamp(math.log1p(citation_velocity) / math.log1p(25))
    recency = clamp((int(year or CURRENT_YEAR) - 2022) / 4.0)

    quality = (
        0.28 * integrity
        + 0.22 * source
        + 0.22 * evidence
        + 0.18 * impact
        + 0.10 * recency
    )
    return {
        "quality_score": round(clamp(quality), 4),
        "integrity_score": round(integrity, 4),
        "source_score": round(source, 4),
        "evidence_score": round(evidence, 4),
        "impact_score": round(impact, 4),
        "recency_score": round(recency, 4),
    }


def query_terms_from_plan(run_dir: Path) -> set[str]:
    plan = read_json(run_dir / "openalex_queries.json")
    if not isinstance(plan, dict):
        return set()
    text_parts = [str(plan.get("description") or "")]
    for query in plan.get("queries") or []:
        if isinstance(query, dict):
            text_parts.append(str(query.get("search") or ""))
            text_parts.append(str(query.get("title_and_abstract.search") or ""))
    return tokenize(" ".join(text_parts))


def relevance_score(paper: dict[str, Any], query_terms: set[str]) -> dict[str, float]:
    if not query_terms:
        return {"relevance_score": 0.0, "title_overlap": 0.0, "abstract_overlap": 0.0, "matched_query_score": 0.0, "noise_penalty": 0.0}
    title_terms = tokenize(paper.get("title") or "")
    abstract_terms = tokenize(paper.get("abstract") or "")
    title_overlap = len(title_terms & query_terms) / max(1, len(query_terms))
    abstract_overlap = len(abstract_terms & query_terms) / max(1, len(query_terms))
    matched_query_score = clamp(len(paper.get("matched_queries") or []) / 3.0)
    title = (paper.get("title") or "").lower()
    noise_terms = ["survey", "review", "challenges", "opportunities", "perspective", "editorial"]
    noise_penalty = 0.12 if any(term in title for term in noise_terms) else 0.0
    score = clamp(0.45 * title_overlap + 0.35 * abstract_overlap + 0.20 * matched_query_score - noise_penalty)
    return {
        "relevance_score": round(score, 4),
        "title_overlap": round(title_overlap, 4),
        "abstract_overlap": round(abstract_overlap, 4),
        "matched_query_score": round(matched_query_score, 4),
        "noise_penalty": round(noise_penalty, 4),
    }


def quality_flags(paper: dict[str, Any], scores: dict[str, float]) -> list[tuple[str, str, str]]:
    flags: list[tuple[str, str, str]] = []
    if paper.get("is_retracted"):
        flags.append(("retracted", "critical", "OpenAlex marks the work as retracted."))
    if paper.get("is_paratext"):
        flags.append(("paratext", "high", "OpenAlex marks the work as paratext, not a regular research article."))
    if not paper.get("doi"):
        flags.append(("missing_doi", "medium", "No DOI found; bibliographic stability is weaker."))
    if len(paper.get("abstract") or "") < 240:
        flags.append(("short_or_missing_abstract", "medium", "Abstract is missing or too short for strong evidence grounding."))
    if not paper.get("source_is_core"):
        flags.append(("non_core_source", "low", "OpenAlex source is not marked core."))
    if scores["evidence_score"] < 0.35:
        flags.append(("weak_evidence_metadata", "medium", "Metadata has limited abstract/reference evidence."))
    if scores["impact_score"] < 0.08 and int(paper.get("publication_year") or CURRENT_YEAR) <= CURRENT_YEAR - 1:
        flags.append(("low_observed_impact", "low", "Older than the current year but has very low citation signal."))
    return flags


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        DROP TABLE IF EXISTS papers;
        DROP TABLE IF EXISTS runs;
        DROP TABLE IF EXISTS paper_runs;
        DROP TABLE IF EXISTS quality_scores;
        DROP TABLE IF EXISTS run_relevance_scores;
        DROP TABLE IF EXISTS quality_flags;

        CREATE TABLE papers (
          openalex_id TEXT PRIMARY KEY,
          doi TEXT,
          title TEXT,
          abstract TEXT,
          publication_year INTEGER,
          publication_date TEXT,
          type TEXT,
          language TEXT,
          cited_by_count INTEGER,
          referenced_works_count INTEGER,
          source_name TEXT,
          source_type TEXT,
          source_is_core INTEGER,
          source_is_oa INTEGER,
          source_is_in_doaj INTEGER,
          host_organization_name TEXT,
          is_retracted INTEGER,
          is_paratext INTEGER,
          is_oa INTEGER,
          oa_status TEXT,
          primary_topic TEXT,
          primary_field TEXT,
          primary_subfield TEXT,
          raw_json TEXT
        );

        CREATE TABLE runs (
          run_id TEXT PRIMARY KEY,
          run_dir TEXT,
          topic_slug TEXT,
          query_terms_json TEXT
        );

        CREATE TABLE paper_runs (
          openalex_id TEXT,
          run_id TEXT,
          matched_queries_json TEXT,
          PRIMARY KEY (openalex_id, run_id)
        );

        CREATE TABLE quality_scores (
          openalex_id TEXT PRIMARY KEY,
          quality_score REAL,
          integrity_score REAL,
          source_score REAL,
          evidence_score REAL,
          impact_score REAL,
          recency_score REAL
        );

        CREATE TABLE run_relevance_scores (
          openalex_id TEXT,
          run_id TEXT,
          relevance_score REAL,
          title_overlap REAL,
          abstract_overlap REAL,
          matched_query_score REAL,
          noise_penalty REAL,
          PRIMARY KEY (openalex_id, run_id)
        );

        CREATE TABLE quality_flags (
          openalex_id TEXT,
          run_id TEXT,
          flag TEXT,
          severity TEXT,
          reason TEXT
        );

        CREATE INDEX idx_quality_score ON quality_scores(quality_score DESC);
        CREATE INDEX idx_relevance_score ON run_relevance_scores(run_id, relevance_score DESC);
        CREATE INDEX idx_papers_year ON papers(publication_year DESC);
        """
    )


def upsert_paper(conn: sqlite3.Connection, paper: dict[str, Any]) -> None:
    conn.execute(
        """
        INSERT OR REPLACE INTO papers VALUES (
          :openalex_id, :doi, :title, :abstract, :publication_year, :publication_date,
          :type, :language, :cited_by_count, :referenced_works_count, :source_name,
          :source_type, :source_is_core, :source_is_oa, :source_is_in_doaj,
          :host_organization_name, :is_retracted, :is_paratext, :is_oa, :oa_status,
          :primary_topic, :primary_field, :primary_subfield, :raw_json
        )
        """,
        paper,
    )


def build_db(runs_dir: Path, out_dir: Path, db_name: str) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    db_path = out_dir / db_name
    conn = sqlite3.connect(db_path)
    init_db(conn)
    seen_papers: set[str] = set()
    flag_counter: Counter[str] = Counter()
    run_count = 0
    paper_run_count = 0

    for run_dir, results_path in discover_exports(runs_dir):
        run_count += 1
        run_id = run_dir.name
        topic_slug = re.sub(r"^\d{8}T\d{6}Z-", "", run_id)
        qterms = query_terms_from_plan(run_dir)
        conn.execute(
            "INSERT OR REPLACE INTO runs VALUES (?, ?, ?, ?)",
            (run_id, str(run_dir), topic_slug, json.dumps(sorted(qterms))),
        )
        for row in read_jsonl(results_path):
            paper = normalize_paper(row)
            if paper is None:
                continue
            openalex_id = paper["openalex_id"]
            upsert_paper(conn, paper)
            seen_papers.add(openalex_id)
            conn.execute(
                "INSERT OR REPLACE INTO paper_runs VALUES (?, ?, ?)",
                (openalex_id, run_id, json.dumps(paper.get("matched_queries") or [])),
            )
            paper_run_count += 1
            qscores = quality_scores(paper)
            conn.execute(
                """
                INSERT OR REPLACE INTO quality_scores VALUES (
                  :openalex_id, :quality_score, :integrity_score, :source_score,
                  :evidence_score, :impact_score, :recency_score
                )
                """,
                {"openalex_id": openalex_id, **qscores},
            )
            rscores = relevance_score(paper, qterms)
            conn.execute(
                """
                INSERT OR REPLACE INTO run_relevance_scores VALUES (
                  :openalex_id, :run_id, :relevance_score, :title_overlap,
                  :abstract_overlap, :matched_query_score, :noise_penalty
                )
                """,
                {"openalex_id": openalex_id, "run_id": run_id, **rscores},
            )
            for flag, severity, reason in quality_flags(paper, qscores):
                flag_counter[flag] += 1
                conn.execute(
                    "INSERT INTO quality_flags VALUES (?, ?, ?, ?, ?)",
                    (openalex_id, run_id, flag, severity, reason),
                )
    conn.commit()
    conn.execute(
        """
        CREATE VIEW IF NOT EXISTS ranked_papers AS
        SELECT
          p.openalex_id, p.title, p.publication_year, p.source_name, p.cited_by_count,
          q.quality_score, q.integrity_score, q.source_score, q.evidence_score,
          q.impact_score, q.recency_score
        FROM papers p
        JOIN quality_scores q ON p.openalex_id = q.openalex_id
        ORDER BY q.quality_score DESC
        """
    )
    conn.execute(
        """
        CREATE VIEW IF NOT EXISTS ranked_run_papers AS
        SELECT
          r.run_id, p.openalex_id, p.title, p.publication_year, p.source_name,
          p.cited_by_count, q.quality_score, rr.relevance_score,
          ROUND(0.55 * rr.relevance_score + 0.45 * q.quality_score, 4) AS retrieval_quality_score
        FROM run_relevance_scores rr
        JOIN papers p ON p.openalex_id = rr.openalex_id
        JOIN quality_scores q ON q.openalex_id = rr.openalex_id
        JOIN runs r ON r.run_id = rr.run_id
        ORDER BY r.run_id, retrieval_quality_score DESC
        """
    )
    conn.commit()
    conn.close()

    manifest = {
        "database": str(db_path),
        "source_runs_dir": str(runs_dir),
        "counts": {
            "runs": run_count,
            "unique_papers": len(seen_papers),
            "paper_run_links": paper_run_count,
            "quality_flags": dict(sorted(flag_counter.items())),
        },
        "quality_model": {
            "quality_score": "0.28 integrity + 0.22 source + 0.22 evidence + 0.18 impact + 0.10 recency",
            "run_retrieval_quality_score": "0.55 run relevance + 0.45 global quality",
            "note": "Heuristic bootstrap scores. Use human/LLM relevance labels later to calibrate weights.",
        },
    }
    (out_dir / "README.md").write_text(readme_text(manifest), encoding="utf-8")
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def readme_text(manifest: dict[str, Any]) -> str:
    return f"""# Paper Retrieval Database

This SQLite database stores papers retrieved by real lit-watch/OpenAlex runs and
adds explainable quality signals.

Database: `{manifest["database"]}`

## What Counts As Paper Quality?

Quality is multi-dimensional:

- `integrity_score`: not retracted, not paratext, English article metadata.
- `source_score`: DOI/source/core venue/source type signals.
- `evidence_score`: title, abstract length, reference count, OA availability.
- `impact_score`: citation count and age-normalized citation velocity.
- `recency_score`: recent papers get a small boost.
- `relevance_score`: run-specific title/abstract/query overlap and matched query count.

The global `quality_score` is only a bootstrap ranking signal:

`{manifest["quality_model"]["quality_score"]}`

For each run, use `ranked_run_papers.retrieval_quality_score`:

`{manifest["quality_model"]["run_retrieval_quality_score"]}`

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
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--db-name", default=DEFAULT_DB_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    manifest = build_db(Path(args.runs_dir), Path(args.out_dir), args.db_name)
    counts = manifest["counts"]
    print(
        f"Built {manifest['database']}: "
        f"{counts['unique_papers']} unique papers from {counts['runs']} runs "
        f"({counts['paper_run_links']} paper-run links)."
    )


if __name__ == "__main__":
    main()
