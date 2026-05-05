#!/usr/bin/env python3
"""Evaluate search quality for a free Workflow run versus a WorkflowIR run.

The existing effectiveness report focuses on execution reliability. This script
adds a retrieval-quality layer for one paired topic by scoring both exported
OpenAlex result sets with the same topic anchors and metadata heuristics.
"""

from __future__ import annotations

import argparse
import json
import math
import re
from pathlib import Path
from typing import Any


DEFAULT_TOPIC = (
    "benchmarks for tool-using LLM agents that evaluate DAG planning, executable workflows, "
    "API-tool selection, dependency edges, and exact-match workflow plans"
)
DEFAULT_ANCHORS = [
    "tool-using LLM agent benchmarks",
    "DAG planning",
    "executable workflows",
    "API tool selection",
    "dependency edges",
    "exact-match workflow plans",
]
DEFAULT_TERM_GROUPS = {
    "agent": ["agent", "agents", "llm agent", "language model agent"],
    "benchmark": ["benchmark", "benchmarks", "evaluation", "evaluate"],
    "workflow": ["workflow", "workflows", "plan", "planning", "dag"],
    "tool": ["tool", "tools", "api", "function calling", "tool use"],
}
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "by",
    "for",
    "from",
    "in",
    "including",
    "into",
    "of",
    "on",
    "or",
    "that",
    "the",
    "to",
    "with",
}
REQUIRED_ARTIFACTS = [
    "openalex/manifest.json",
    "openalex/all_results_deduped.jsonl",
    "SUMMARY.md",
]
WORKFLOWIR_ARTIFACTS = [
    "workflow_ir.json",
    "workflow_trace.jsonl",
    "openalex_queries.initial.json",
    "openalex_queries.final.json",
    "dry_run/query_counts.csv",
    "RETRIEVAL_EVAL.json",
    "QUALITY_NOTES.md",
    "AGENT_DECISIONS.jsonl",
]


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    return payload if isinstance(payload, dict) else {}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if not path.exists():
        return rows
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError:
                continue
            if isinstance(payload, dict):
                rows.append(payload)
    return rows


def slugify(value: str, max_length: int = 80) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if len(value) > max_length:
        value = value[:max_length].rstrip("-._")
    return value or "topic"


def normalize_text(value: Any) -> str:
    if value is None:
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()


def nested_get(payload: dict[str, Any], path: list[str]) -> Any:
    current: Any = payload
    for key in path:
        if not isinstance(current, dict):
            return None
        current = current.get(key)
    return current


def topic_strings(work: dict[str, Any]) -> list[str]:
    output: list[str] = []
    primary = work.get("primary_topic")
    if isinstance(primary, dict):
        for path in [
            ["display_name"],
            ["domain", "display_name"],
            ["field", "display_name"],
            ["subfield", "display_name"],
        ]:
            output.append(normalize_text(nested_get(primary, path)))
    topics = work.get("topics")
    if isinstance(topics, list):
        for topic in topics[:5]:
            if isinstance(topic, dict):
                output.append(normalize_text(topic.get("display_name")))
    return [item for item in output if item]


def source_name(work: dict[str, Any], row: dict[str, Any]) -> str:
    for candidate in [
        row.get("source"),
        row.get("source_display_name"),
        nested_get(work, ["primary_location", "source", "display_name"]),
        nested_get(work, ["best_oa_location", "source", "display_name"]),
        nested_get(work, ["primary_location", "raw_source_name"]),
        nested_get(work, ["best_oa_location", "raw_source_name"]),
    ]:
        text = normalize_text(candidate)
        if text:
            return text
    return ""


def is_core_source(work: dict[str, Any]) -> bool:
    for path in [
        ["primary_location", "source", "is_core"],
        ["best_oa_location", "source", "is_core"],
    ]:
        value = nested_get(work, path)
        if value is True:
            return True
    return False


def normalized_work(row: dict[str, Any]) -> dict[str, Any]:
    work = row.get("work") if isinstance(row.get("work"), dict) else row
    return {
        "title": normalize_text(row.get("title") or work.get("title") or work.get("display_name")),
        "abstract": normalize_text(row.get("abstract") or work.get("abstract")),
        "doi": normalize_text(row.get("doi") or work.get("doi")),
        "year": int(row.get("publication_year") or work.get("publication_year") or 0),
        "cited_by_count": int(row.get("cited_by_count") or work.get("cited_by_count") or 0),
        "source": source_name(work, row),
        "is_core_source": is_core_source(work),
        "matched_queries": row.get("matched_queries") if isinstance(row.get("matched_queries"), list) else [],
        "topics": topic_strings(work),
        "openalex_id": normalize_text(row.get("openalex_id") or work.get("id")),
    }


def searchable_text(work: dict[str, Any]) -> str:
    parts = [
        work["title"],
        work["abstract"],
        work["source"],
        " ".join(work["topics"]),
        " ".join(str(item) for item in work["matched_queries"]),
    ]
    return " ".join(parts).lower()


def words(value: str) -> list[str]:
    return [word for word in re.findall(r"[a-z0-9]+", value.lower()) if word not in STOPWORDS]


def phrase_hit(text: str, phrase: str) -> bool:
    phrase = phrase.lower().strip()
    if not phrase:
        return False
    if " " in phrase and phrase in text:
        return True
    tokens = words(phrase)
    if not tokens:
        return False
    hits = sum(1 for token in tokens if token in text)
    if len(tokens) == 1:
        return hits == 1
    if len(tokens) == 2:
        return hits == 2
    threshold = 0.75 if len(tokens) <= 4 else 0.60
    return hits >= math.ceil(len(tokens) * threshold)


def score_work(work: dict[str, Any], anchors: list[str], term_groups: dict[str, list[str]]) -> dict[str, Any]:
    text = searchable_text(work)
    anchor_hits = [anchor for anchor in anchors if phrase_hit(text, anchor)]
    anchor_score = len(anchor_hits) / max(1, len(anchors))
    group_hits = 0
    for phrases in term_groups.values():
        if any(phrase_hit(text, phrase) for phrase in phrases):
            group_hits += 1
    group_score = group_hits / max(1, len(term_groups))
    relevance = round(0.65 * anchor_score + 0.35 * group_score, 4)

    citation_score = min(1.0, math.log1p(work["cited_by_count"]) / math.log1p(100))
    has_doi = 1.0 if work["doi"] else 0.0
    has_abstract = 1.0 if work["abstract"] else 0.0
    recency = 1.0 if work["year"] >= 2025 else 0.8 if work["year"] >= 2024 else 0.45 if work["year"] else 0.0
    venue_signal = 1.0 if work["is_core_source"] else 0.6 if work["source"] else 0.0
    quality = round(
        0.25 * citation_score + 0.25 * has_abstract + 0.15 * has_doi + 0.20 * recency + 0.15 * venue_signal,
        4,
    )
    combined = round(0.65 * relevance + 0.35 * quality, 4)
    return {
        "relevance_score": relevance,
        "quality_score": quality,
        "combined_score": combined,
        "anchor_hits": anchor_hits,
        "term_group_hits": group_hits,
        "has_doi": bool(has_doi),
        "has_abstract": bool(has_abstract),
    }


def relevance_label(score: float) -> str:
    if score >= 0.60:
        return "core"
    if score >= 0.35:
        return "supporting"
    if score >= 0.15:
        return "peripheral"
    return "off_topic"


def mean(values: list[float]) -> float | None:
    if not values:
        return None
    return round(sum(values) / len(values), 4)


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def artifact_metrics(run_dir: Path, is_workflowir: bool) -> dict[str, Any]:
    required = REQUIRED_ARTIFACTS + (WORKFLOWIR_ARTIFACTS if is_workflowir else [])
    present = [relative for relative in required if (run_dir / relative).exists()]
    missing = [relative for relative in required if not (run_dir / relative).exists()]
    return {
        "required_artifacts": len(required),
        "present_artifacts": len(present),
        "missing_artifacts": missing,
        "artifact_pass_rate": ratio(len(present), len(required)),
    }


def query_metrics(manifest: dict[str, Any], broad_threshold: int) -> dict[str, Any]:
    queries = manifest.get("queries") if isinstance(manifest.get("queries"), list) else []
    reported = [int(query.get("reported_count") or 0) for query in queries if isinstance(query, dict)]
    downloaded = [int(query.get("downloaded_count") or 0) for query in queries if isinstance(query, dict)]
    return {
        "query_count": len(queries),
        "total_reported_count": sum(reported),
        "total_downloaded_rows": manifest.get("total_downloaded_rows") or sum(downloaded),
        "total_deduped_works": manifest.get("total_deduped_works"),
        "mean_reported_per_query": mean([float(value) for value in reported]),
        "max_reported_query": max(reported) if reported else None,
        "too_broad_queries": sum(1 for value in reported if value > broad_threshold),
        "zero_result_queries": sum(1 for value in reported if value == 0),
        "empty_download_queries": sum(1 for value in downloaded if value == 0),
    }


def evaluate_run(
    label: str,
    run_dir: Path,
    anchors: list[str],
    term_groups: dict[str, list[str]],
    top_k: int,
    broad_threshold: int,
    is_workflowir: bool,
) -> dict[str, Any]:
    manifest = read_json(run_dir / "openalex" / "manifest.json") if (run_dir / "openalex" / "manifest.json").exists() else {}
    rows = iter_jsonl(run_dir / "openalex" / "all_results_deduped.jsonl")
    scored: list[dict[str, Any]] = []
    for row in rows:
        work = normalized_work(row)
        score = score_work(work, anchors, term_groups)
        scored.append({**work, **score, "relevance": relevance_label(score["relevance_score"])})
    scored.sort(key=lambda item: item["combined_score"], reverse=True)
    top = scored[:top_k]
    covered_anchors = sorted({anchor for item in top for anchor in item["anchor_hits"]})
    core = sum(1 for item in top if item["relevance"] == "core")
    supporting_or_core = sum(1 for item in top if item["relevance"] in {"core", "supporting"})
    off_topic = sum(1 for item in top if item["relevance"] == "off_topic")
    metrics = {
        **query_metrics(manifest, broad_threshold),
        **artifact_metrics(run_dir, is_workflowir),
        "result_rows": len(scored),
        "top_k": top_k,
        "mean_relevance_at_k": mean([item["relevance_score"] for item in top]),
        "mean_quality_at_k": mean([item["quality_score"] for item in top]),
        "mean_combined_at_k": mean([item["combined_score"] for item in top]),
        "core_at_k": ratio(core, len(top)),
        "supporting_or_core_at_k": ratio(supporting_or_core, len(top)),
        "off_topic_at_k": ratio(off_topic, len(top)),
        "doi_rate_at_k": ratio(sum(1 for item in top if item["has_doi"]), len(top)),
        "abstract_rate_at_k": ratio(sum(1 for item in top if item["has_abstract"]), len(top)),
        "anchor_coverage_at_k": ratio(len(covered_anchors), len(anchors)),
        "covered_anchors_at_k": covered_anchors,
    }
    return {
        "label": label,
        "run_dir": str(run_dir),
        "manifest_path": str(run_dir / "openalex" / "manifest.json"),
        "metrics": metrics,
        "top_papers": [
            {
                "rank": index,
                "title": item["title"],
                "year": item["year"],
                "source": item["source"],
                "doi": item["doi"],
                "relevance": item["relevance"],
                "relevance_score": item["relevance_score"],
                "quality_score": item["quality_score"],
                "combined_score": item["combined_score"],
                "anchor_hits": item["anchor_hits"],
                "matched_queries": item["matched_queries"],
            }
            for index, item in enumerate(top[:10], start=1)
        ],
    }


def metric_delta(workflowir: Any, workflow: Any) -> Any:
    if isinstance(workflowir, (int, float)) and isinstance(workflow, (int, float)):
        return round(float(workflowir) - float(workflow), 4)
    return None


def comparison_payload(topic: str, anchors: list[str], workflow: dict[str, Any], workflowir: dict[str, Any]) -> dict[str, Any]:
    keys = sorted(set(workflow["metrics"]) | set(workflowir["metrics"]))
    return {
        "topic": topic,
        "anchors": anchors,
        "workflow": workflow,
        "workflowir": workflowir,
        "deltas": {
            key: metric_delta(workflowir["metrics"].get(key), workflow["metrics"].get(key))
            for key in keys
        },
    }


def is_rate_metric(key: str) -> bool:
    return (
        key.endswith("_rate")
        or key.endswith("_at_k")
        or key in {"mean_relevance_at_k", "mean_quality_at_k", "mean_combined_at_k"}
    )


def fmt_metric(key: str, value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        if is_rate_metric(key):
            return f"{value:.1%}"
        if value.is_integer():
            return str(int(value))
        return f"{value:.3f}"
    return str(value)


def esc(value: Any) -> str:
    return normalize_text(value).replace("|", "\\|")


def report_markdown(payload: dict[str, Any], json_path: Path) -> str:
    workflow = payload["workflow"]
    workflowir = payload["workflowir"]
    deltas = payload["deltas"]
    metric_rows = [
        ("total_deduped_works", "Coverage size", "larger is broader, not always better"),
        ("query_count", "Query families", "2-5 is expected"),
        ("too_broad_queries", "Too-broad queries", "lower is better"),
        ("zero_result_queries", "Zero-result queries", "lower is better"),
        ("mean_relevance_at_k", "Mean relevance@k", "higher is better"),
        ("core_at_k", "Core@k", "higher is better"),
        ("supporting_or_core_at_k", "Core/supporting@k", "higher is better"),
        ("off_topic_at_k", "Off-topic@k", "lower is better"),
        ("anchor_coverage_at_k", "Anchor coverage@k", "higher is better"),
        ("mean_quality_at_k", "Mean quality@k", "higher is better"),
        ("mean_combined_at_k", "Mean combined@k", "higher is better"),
        ("present_artifacts", "Audit artifacts present", "higher is better for auditability"),
        ("artifact_pass_rate", "Artifact pass rate", "higher is better"),
    ]
    lines = [
        "# Workflow vs WorkflowIR Search Quality Evaluation",
        "",
        f"Topic: {payload['topic']}",
        "",
        "## Inputs",
        "",
        f"- Workflow run: `{workflow['run_dir']}`",
        f"- WorkflowIR run: `{workflowir['run_dir']}`",
        f"- Machine-readable report: `{json_path}`",
        "",
        "## Metric Comparison",
        "",
        "| Metric | Workflow | WorkflowIR | Delta | Note |",
        "|---|---:|---:|---:|---|",
    ]
    for key, label, note in metric_rows:
        lines.append(
            f"| {label} | {fmt_metric(key, workflow['metrics'].get(key))} | "
            f"{fmt_metric(key, workflowir['metrics'].get(key))} | {fmt_metric(key, deltas.get(key))} | {note} |"
        )

    lines.extend(
        [
            "",
            "## Top Retrieved Papers",
            "",
            "| Rank | Workflow | Score | WorkflowIR | Score |",
            "|---:|---|---:|---|---:|",
        ]
    )
    top_workflow = workflow["top_papers"]
    top_workflowir = workflowir["top_papers"]
    for index in range(max(len(top_workflow), len(top_workflowir))):
        left = top_workflow[index] if index < len(top_workflow) else {}
        right = top_workflowir[index] if index < len(top_workflowir) else {}
        lines.append(
            f"| {index + 1} | {esc(left.get('title', ''))} | {fmt_metric('mean_combined_at_k', left.get('combined_score'))} | "
            f"{esc(right.get('title', ''))} | {fmt_metric('mean_combined_at_k', right.get('combined_score'))} |"
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            interpret(payload),
            "",
        ]
    )
    return "\n".join(lines)


def interpret(payload: dict[str, Any]) -> str:
    workflow = payload["workflow"]["metrics"]
    workflowir = payload["workflowir"]["metrics"]
    points: list[str] = []
    if (workflowir.get("too_broad_queries") or 0) < (workflow.get("too_broad_queries") or 0):
        points.append("WorkflowIR used tighter query control: it produced fewer over-broad query families.")
    if (workflowir.get("present_artifacts") or 0) > (workflow.get("present_artifacts") or 0):
        points.append("WorkflowIR produced a stronger audit trail because it generated more checkable intermediate artifacts.")
    if (workflowir.get("mean_relevance_at_k") or 0) >= (workflow.get("mean_relevance_at_k") or 0):
        points.append("WorkflowIR is at least competitive on top-k semantic relevance under the shared heuristic.")
    else:
        points.append("The free Workflow run has higher heuristic top-k relevance on this pair, so the claim should be framed as reliability plus auditability, not universal semantic superiority.")
    if (workflow.get("total_deduped_works") or 0) > (workflowir.get("total_deduped_works") or 0):
        points.append("Workflow retrieved a broader pool; this can help recall, but it also increases manual screening cost.")
    return "\n".join(f"- {point}" for point in points)


def parse_term_groups(values: list[str] | None) -> dict[str, list[str]]:
    if not values:
        return DEFAULT_TERM_GROUPS
    groups: dict[str, list[str]] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"Term group must look like name=term1,term2: {value}")
        name, raw_terms = value.split("=", 1)
        terms = [term.strip() for term in raw_terms.split(",") if term.strip()]
        if terms:
            groups[name.strip()] = terms
    return groups or DEFAULT_TERM_GROUPS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--topic", default=DEFAULT_TOPIC)
    parser.add_argument("--anchor", action="append", dest="anchors", help="Topic anchor. Repeatable.")
    parser.add_argument("--term-group", action="append", help="Relevance group as name=term1,term2. Repeatable.")
    parser.add_argument("--workflow-run-dir", required=True)
    parser.add_argument("--workflowir-run-dir", required=True)
    parser.add_argument("--out-dir", default="data/workflowir_litsearch_eval")
    parser.add_argument("--top-k", type=int, default=20)
    parser.add_argument("--broad-count-threshold", type=int, default=300)
    parser.add_argument("--output-prefix", default=None)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    topic = str(args.topic).strip()
    anchors = args.anchors or DEFAULT_ANCHORS
    term_groups = parse_term_groups(args.term_group)
    workflow_run_dir = Path(args.workflow_run_dir).resolve()
    workflowir_run_dir = Path(args.workflowir_run_dir).resolve()
    workflow = evaluate_run(
        "Workflow",
        workflow_run_dir,
        anchors,
        term_groups,
        args.top_k,
        args.broad_count_threshold,
        is_workflowir=False,
    )
    workflowir = evaluate_run(
        "WorkflowIR",
        workflowir_run_dir,
        anchors,
        term_groups,
        args.top_k,
        args.broad_count_threshold,
        is_workflowir=True,
    )
    payload = comparison_payload(topic, anchors, workflow, workflowir)
    out_dir = Path(args.out_dir)
    prefix = args.output_prefix or f"workflow_vs_workflowir_search_quality_{slugify(topic, 48)}"
    json_path = out_dir / f"{prefix}.json"
    md_path = out_dir / f"{prefix}.md"
    write_json(json_path, payload)
    md_path.parent.mkdir(parents=True, exist_ok=True)
    md_path.write_text(report_markdown(payload, json_path), encoding="utf-8")
    print(f"Wrote {json_path}")
    print(f"Wrote {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
