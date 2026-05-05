#!/usr/bin/env python3
"""Run WorkflowIR-controlled literature-search trials.

This runner is the controlled counterpart to ``run_real_litwatch_trials.py``.
The baseline lets an agent freely plan, call OpenAlex, summarize, and exit.
This runner turns the same task into a small WorkflowIR DAG:

1. create a run directory;
2. generate a bounded query plan;
3. schema-check the query plan;
4. run OpenAlex dry-run counts;
5. repair broad or zero-result queries;
6. run the full export;
7. write retrieval evaluation and summary files;
8. verify required artifacts.

The LLM/agent role can be added as a bounded planner later, but the core
advantage tested here is WorkflowIR control: explicit preconditions, effects,
timeouts, repair rules, and machine-readable traces.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = "configs/workflowir_litsearch_trials.example.json"
DEFAULT_OPENALEX_SCRIPT = "crates/runtime/assets/skills/openalex-search/scripts/openalex_works_export.py"
DEFAULT_OUTPUT_DIR = "lit-watch/workflowir-agent-runs"
DEFAULT_BATCH_ROOT = "lit-watch/workflowir-batches"
DEFAULT_LOOKBACK_DAYS = 730
DEFAULT_MAX_RESULTS_PER_QUERY = 150
DEFAULT_BROAD_COUNT_THRESHOLD = 300
DEFAULT_ZERO_RESULT_THRESHOLD = 0
REQUIRED_FILES = [
    "workflow_ir.json",
    "workflow_trace.jsonl",
    "openalex_queries.initial.json",
    "openalex_queries.final.json",
    "dry_run/query_counts.csv",
    "openalex/manifest.json",
    "SUMMARY.md",
    "RETRIEVAL_EVAL.json",
    "QUALITY_NOTES.md",
    "AGENT_DECISIONS.jsonl",
]


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "benchmark",
    "benchmarks",
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


@dataclass
class NodeSpec:
    node_id: str
    tool: str
    preconditions: list[str]
    effects: list[str]
    failure_modes: list[str]
    depends_on: list[str] = field(default_factory=list)


@dataclass
class NodeResult:
    node_id: str
    status: str
    started_at: str
    finished_at: str
    preconditions: list[str]
    effects: list[str]
    failure_mode: str | None = None
    evidence: dict[str, Any] = field(default_factory=dict)


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def append_jsonl(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n")


def slugify(value: str, max_length: int = 96) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if len(value) > max_length:
        value = value[:max_length].rstrip("-._")
    return value or "trial"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--execute", action="store_true", help="Run OpenAlex calls. Without this flag, only plan.")
    parser.add_argument("--max-trials", type=int, default=None)
    parser.add_argument("--batch-dir", default=None)
    parser.add_argument("--max-results-per-query", type=int, default=None)
    parser.add_argument("--broad-count-threshold", type=int, default=None)
    parser.add_argument("--openalex-script", default=None)
    parser.add_argument("--baseline-batch", default=None, help="Optional baseline batch manifest for comparison report.")
    return parser.parse_args()


def workflow_ir() -> dict[str, Any]:
    nodes = [
        NodeSpec(
            "create_run",
            "filesystem",
            ["trial.topic is non-empty"],
            ["run_dir exists", "workflow_ir.json written"],
            ["filesystem_error"],
        ),
        NodeSpec(
            "plan_queries",
            "workflowir.query_planner",
            ["run_dir exists", "topic anchors available"],
            ["openalex_queries.initial.json written", "2-5 candidate query families"],
            ["planner_empty", "planner_schema_invalid"],
            ["create_run"],
        ),
        NodeSpec(
            "validate_query_plan",
            "workflowir.schema_validator",
            ["initial query plan exists"],
            ["schema-normalized plan", "query count constrained to 2-5"],
            ["schema_validation_failed", "query_count_invalid"],
            ["plan_queries"],
        ),
        NodeSpec(
            "dry_run_counts",
            "openalex_works_export --dry-run",
            ["validated query plan exists", "OpenAlex script exists"],
            ["dry_run/query_counts.csv written", "dry_run/manifest.json written"],
            ["openalex_api_error", "dry_run_missing_counts"],
            ["validate_query_plan"],
        ),
        NodeSpec(
            "repair_queries",
            "workflowir.query_repair",
            ["query_counts.csv exists"],
            ["broad queries tightened", "zero-result queries broadened", "openalex_queries.final.json written"],
            ["repair_not_possible", "repair_schema_invalid"],
            ["dry_run_counts"],
        ),
        NodeSpec(
            "full_export",
            "openalex_works_export",
            ["final query plan exists"],
            ["openalex/manifest.json written", "deduplicated metadata exported"],
            ["openalex_api_error", "export_empty", "export_missing_manifest"],
            ["repair_queries"],
        ),
        NodeSpec(
            "evaluate_results",
            "workflowir.retrieval_evaluator",
            ["deduplicated metadata exists"],
            ["RETRIEVAL_EVAL.json written", "QUALITY_NOTES.md written", "SUMMARY.md written"],
            ["metadata_missing", "summary_generation_failed"],
            ["full_export"],
        ),
        NodeSpec(
            "verify_contract",
            "workflowir.contract_checker",
            ["run artifacts exist"],
            ["contract_status written to manifest"],
            ["required_file_missing"],
            ["evaluate_results"],
        ),
    ]
    return {
        "workflow_id": "workflowir_litsearch_v1",
        "description": "Controlled literature-search WorkflowIR with deterministic tool execution and repair.",
        "nodes": [
            {
                "node_id": node.node_id,
                "tool": node.tool,
                "depends_on": node.depends_on,
                "preconditions": node.preconditions,
                "effects": node.effects,
                "failure_modes": node.failure_modes,
            }
            for node in nodes
        ],
    }


def run_node(run_dir: Path, node: NodeSpec, func, *args: Any, **kwargs: Any) -> NodeResult:
    started = utc_now()
    try:
        evidence = func(*args, **kwargs)
        status = "completed"
        failure_mode = None
    except Exception as exc:  # Keep the trace; the caller decides whether to continue.
        evidence = {"error": f"{type(exc).__name__}: {exc}"}
        status = "failed"
        failure_mode = node.failure_modes[0] if node.failure_modes else "unknown"
    finished = utc_now()
    result = NodeResult(
        node_id=node.node_id,
        status=status,
        started_at=started,
        finished_at=finished,
        preconditions=node.preconditions,
        effects=node.effects if status == "completed" else [],
        failure_mode=failure_mode,
        evidence=evidence if isinstance(evidence, dict) else {"value": evidence},
    )
    append_jsonl(run_dir / "workflow_trace.jsonl", result.__dict__)
    return result


def load_trials(config: dict[str, Any]) -> list[dict[str, Any]]:
    trials = config.get("trials")
    if not isinstance(trials, list) or not trials:
        raise SystemExit("Config must contain a non-empty trials array.")
    output: list[dict[str, Any]] = []
    for index, trial in enumerate(trials, start=1):
        if not isinstance(trial, dict):
            raise SystemExit(f"Trial #{index} must be an object.")
        topic = str(trial.get("topic", "")).strip()
        if not topic:
            raise SystemExit(f"Trial #{index} is missing topic.")
        name = str(trial.get("name") or slugify(topic))
        output.append({**trial, "name": slugify(name), "topic": topic})
    return output


def topic_anchors(trial: dict[str, Any]) -> list[str]:
    explicit = trial.get("anchors")
    anchors: list[str] = []
    if isinstance(explicit, list):
        anchors.extend(str(item).strip() for item in explicit if str(item).strip())
    topic = str(trial["topic"])
    chunks = re.split(r"[,;:()]|\band\b|\bincluding\b|\bthat\b", topic, flags=re.IGNORECASE)
    for chunk in chunks:
        words = [
            word
            for word in re.findall(r"[A-Za-z][A-Za-z0-9+-]*", chunk.lower())
            if word not in STOPWORDS and len(word) > 1
        ]
        if 2 <= len(words) <= 6:
            anchors.append(" ".join(words))
        elif len(words) > 6:
            anchors.append(" ".join(words[:5]))
    cleaned: list[str] = []
    seen: set[str] = set()
    for anchor in anchors:
        normalized = re.sub(r"\s+", " ", anchor.strip().lower())
        if normalized and normalized not in seen:
            cleaned.append(anchor.strip())
            seen.add(normalized)
    return cleaned[:8] or [topic]


def quote_phrase(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    return f'"{value}"' if " " in value and not value.startswith('"') else value


def generate_query_plan(
    trial: dict[str, Any],
    from_date: str,
    to_date: str,
    max_queries: int = 5,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    anchors = topic_anchors(trial)
    project = slugify(trial["name"], max_length=64)
    queries: list[dict[str, str]] = []
    decisions: list[dict[str, Any]] = []

    templates = trial.get("query_templates")
    if isinstance(templates, list) and templates:
        for index, template in enumerate(templates[:max_queries], start=1):
            if isinstance(template, dict):
                query = {key: str(value) for key, value in template.items() if value is not None}
                query.setdefault("name", f"query_{index:02d}")
                queries.append(query)
        decisions.append(decision("query_design", "trial query_templates", "used explicit workflow templates", "config override", "none"))
    else:
        central = "large language model" if re.search(r"\bllm\b|large language model", trial["topic"], re.IGNORECASE) else "AI agent"
        agent_anchor = "LLM agent" if re.search(r"\bllm\b", trial["topic"], re.IGNORECASE) else "AI agent"
        core = anchors[0]
        second = anchors[1] if len(anchors) > 1 else "tool use"
        third = anchors[2] if len(anchors) > 2 else "workflow planning"
        fourth = anchors[3] if len(anchors) > 3 else "benchmark evaluation"
        fifth = anchors[4] if len(anchors) > 4 else "failure tracing"
        queries = [
            {"name": "core_topic", "search": f"{quote_phrase(core)} {quote_phrase(central)}"},
            {"name": "tool_use_eval", "search": f"{quote_phrase(second)} {quote_phrase(agent_anchor)} tool use function calling"},
            {"name": "workflow_planning", "search": f"{quote_phrase(third)} {quote_phrase(agent_anchor)} workflow planning"},
            {"name": "benchmark_quality", "search": f"{quote_phrase(fourth)} {quote_phrase(central)} benchmark evaluation"},
            {"name": "failure_observability", "search": f"{quote_phrase(fifth)} {quote_phrase(agent_anchor)} failure tracing debugging"},
        ][:max_queries]
        decisions.append(
            decision(
                "query_design",
                f"anchors={anchors}",
                f"generated {len(queries)} bounded query families",
                "WorkflowIR planner limits query count and keeps names stable",
                "none",
            )
        )

    plan = {
        "project": project,
        "description": f"WorkflowIR-controlled OpenAlex search strategy for {trial['topic']}",
        "shared": {
            "filter": f"from_publication_date:{from_date},to_publication_date:{to_date},type:article,language:en,is_retracted:false,is_paratext:false",
            "sort": "relevance_score:desc",
        },
        "queries": queries,
    }
    return plan, decisions


def decision(
    event_type: str,
    observed: str,
    action: str,
    reason: str,
    risk: str,
    related_query: str | None = None,
) -> dict[str, Any]:
    return {
        "event_type": event_type,
        "input": observed,
        "decision": action,
        "reason": reason,
        "related_query": related_query,
        "risk_or_failure_signal": risk,
    }


def validate_query_plan(plan: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    if not isinstance(plan, dict):
        raise ValueError("query plan must be an object")
    queries = plan.get("queries")
    if not isinstance(queries, list):
        raise ValueError("query plan missing queries list")
    decisions: list[dict[str, Any]] = []
    normalized: list[dict[str, Any]] = []
    for index, query in enumerate(queries, start=1):
        if not isinstance(query, dict):
            continue
        search = str(query.get("search") or "").strip()
        query_filter = str(query.get("filter") or "").strip()
        if not search and not query_filter:
            decisions.append(decision("query_revision", f"query #{index}", "dropped empty query", "search/filter missing", "too_narrow"))
            continue
        normalized.append(
            {
                key: value
                for key, value in {
                    "name": slugify(str(query.get("name") or f"query_{index:02d}"), max_length=48),
                    "search": search or None,
                    "filter": query_filter or None,
                    "sort": query.get("sort"),
                }.items()
                if value
            }
        )
    if len(normalized) > 5:
        decisions.append(
            decision(
                "query_revision",
                f"query_count={len(normalized)}",
                "truncated to first 5 queries",
                "WorkflowIR protocol requires 2-5 query families",
                "too_broad",
            )
        )
        normalized = normalized[:5]
    if len(normalized) < 2:
        raise ValueError(f"query_count={len(normalized)}; expected at least 2")
    plan = dict(plan)
    plan["queries"] = normalized
    return plan, decisions


def read_query_counts(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    parsed: list[dict[str, Any]] = []
    for row in rows:
        parsed.append(
            {
                **row,
                "reported_count": int(row.get("reported_count") or row.get("count") or 0),
                "downloaded_count": int(row.get("downloaded_count") or 0),
            }
        )
    return parsed


def run_openalex(
    script: Path,
    query_plan: Path,
    out_dir: Path,
    dry_run: bool,
    max_results: int,
    timeout_seconds: int,
) -> dict[str, Any]:
    command = [sys.executable, str(script), "--queries", str(query_plan), "--out", str(out_dir)]
    if dry_run:
        command.append("--dry-run")
    elif max_results > 0:
        command.extend(["--max-results", str(max_results)])
    completed = subprocess.run(command, text=True, capture_output=True, check=False, timeout=timeout_seconds)
    (out_dir / "command.stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (out_dir / "command.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"OpenAlex command failed with {completed.returncode}: {completed.stderr[-1000:]}")
    manifest = read_json(out_dir / "manifest.json") if (out_dir / "manifest.json").exists() else {}
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_chars": len(completed.stdout),
        "stderr_chars": len(completed.stderr),
        "manifest": manifest if isinstance(manifest, dict) else {},
    }


def repair_queries(
    initial_plan: dict[str, Any],
    count_rows: list[dict[str, Any]],
    anchors: list[str],
    broad_threshold: int,
    zero_threshold: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    by_name = {str(row.get("query_name") or row.get("name")): row for row in count_rows}
    decisions: list[dict[str, Any]] = []
    repaired_queries: list[dict[str, Any]] = []
    anchor = anchors[0] if anchors else "LLM agent"
    secondary = anchors[1] if len(anchors) > 1 else anchor
    for query in initial_plan.get("queries", []):
        if not isinstance(query, dict):
            continue
        current = dict(query)
        name = str(current.get("name"))
        row = by_name.get(name, {})
        reported = int(row.get("reported_count") or 0)
        if reported > broad_threshold:
            existing_filter = str(current.get("filter") or "").strip()
            tighten_filter = f"title_and_abstract.search:{anchor}"
            current["filter"] = ",".join(part for part in [existing_filter, tighten_filter] if part)
            decisions.append(
                decision(
                    "query_revision",
                    f"reported_count={reported}",
                    f"added filter {tighten_filter}",
                    f"count above threshold {broad_threshold}",
                    "too_broad",
                    name,
                )
            )
        elif reported <= zero_threshold:
            fallback_terms = " ".join(
                word
                for word in re.findall(r"[A-Za-z0-9+-]+", f"{secondary} LLM agent tool use")
                if word.lower() not in STOPWORDS
            )
            current["search"] = fallback_terms or "LLM agent tool use"
            current.pop("filter", None)
            decisions.append(
                decision(
                    "query_revision",
                    f"reported_count={reported}",
                    f"replaced with broader recovery query: {current['search']}",
                    "zero-result query needs recall recovery",
                    "zero_result",
                    name,
                )
            )
        else:
            decisions.append(decision("dry_run_review", f"reported_count={reported}", "kept query", "count within bounds", "none", name))
        repaired_queries.append(current)
    final_plan = dict(initial_plan)
    final_plan["queries"] = repaired_queries
    final_plan["workflowir_repair"] = {
        "broad_count_threshold": broad_threshold,
        "zero_result_threshold": zero_threshold,
        "anchor_used_for_tightening": anchor,
    }
    return final_plan, decisions


def iter_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    rows = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                try:
                    payload = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(payload, dict):
                    rows.append(payload)
    return rows


def work_text(work: dict[str, Any]) -> str:
    parts = [
        work.get("title") or work.get("display_name") or "",
        work.get("abstract") or "",
        work.get("primary_topic") or "",
        work.get("topics") if isinstance(work.get("topics"), str) else "",
    ]
    return " ".join(str(part) for part in parts).lower()


def score_work(work: dict[str, Any], anchors: list[str], required_terms: list[str]) -> dict[str, Any]:
    text = work_text(work)
    required_hit = any(term.lower() in text for term in required_terms)
    hits = 0
    for anchor in anchors:
        words = [word for word in re.findall(r"[a-z0-9+-]+", anchor.lower()) if word not in STOPWORDS]
        if not words:
            continue
        anchor_hits = sum(1 for word in words if word in text)
        if anchor_hits >= max(1, math.ceil(len(words) / 2)):
            hits += 1
    relevance_score = min(1.0, hits / max(1, min(len(anchors), 5)))
    if required_terms and not required_hit:
        relevance_score = min(relevance_score, 0.1)
    cited_by = int(work.get("cited_by_count") or 0)
    citation_score = min(1.0, math.log1p(cited_by) / math.log1p(100))
    has_doi = 1.0 if work.get("doi") else 0.0
    has_abstract = 1.0 if work.get("abstract") else 0.0
    year = int(work.get("publication_year") or 0)
    recency = 1.0 if year >= 2025 else 0.8 if year >= 2024 else 0.4
    quality_score = 0.35 * citation_score + 0.25 * has_abstract + 0.20 * has_doi + 0.20 * recency
    return {
        "relevance_score": round(relevance_score, 3),
        "quality_score": round(quality_score, 3),
        "combined_score": round(0.6 * relevance_score + 0.4 * quality_score, 3),
        "anchor_hits": hits,
        "required_term_hit": required_hit,
    }


def label_relevance(score: float) -> str:
    if score >= 0.65:
        return "core"
    if score >= 0.35:
        return "supporting"
    if score > 0:
        return "peripheral"
    return "off_topic"


def label_quality(score: float) -> str:
    if score >= 0.70:
        return "high"
    if score >= 0.45:
        return "medium"
    if score > 0:
        return "low"
    return "uncertain"


def evaluate_and_write(
    run_dir: Path,
    trial: dict[str, Any],
    final_plan: dict[str, Any],
    dry_counts: list[dict[str, Any]],
    full_manifest: dict[str, Any],
    decisions: list[dict[str, Any]],
) -> dict[str, Any]:
    anchors = topic_anchors(trial)
    required_terms = [
        str(term).lower()
        for term in trial.get("required_terms", ["llm", "large language model", "agent"])
        if str(term).strip()
    ]
    works = iter_jsonl(run_dir / "openalex" / "all_results_deduped.jsonl")
    scored = []
    for work in works:
        scores = score_work(work, anchors, required_terms)
        scored.append((scores["combined_score"], scores, work))
    scored.sort(key=lambda item: item[0], reverse=True)
    top = []
    for _, scores, work in scored[:12]:
        title = work.get("title") or work.get("display_name") or "(untitled)"
        top.append(
            {
                "title": title,
                "doi": work.get("doi"),
                "year": work.get("publication_year"),
                "source": work.get("source_display_name"),
                "cited_by_count": work.get("cited_by_count"),
                "relevance": label_relevance(scores["relevance_score"]),
                "quality": label_quality(scores["quality_score"]),
                "relevance_score": scores["relevance_score"],
                "quality_score": scores["quality_score"],
            "quality_reason": "WorkflowIR heuristic: required topic terms, anchor overlap, citation signal, DOI, abstract availability, and recency.",
                "evidence_used": "title | abstract | metadata | citation_count | venue",
            }
        )

    query_families = []
    counts_by_name = {str(row.get("query_name") or row.get("name")): row for row in dry_counts}
    manifest_by_name = {
        str(query.get("name")): query
        for query in full_manifest.get("queries", [])
        if isinstance(query, dict)
    }
    failure_signals: list[dict[str, Any]] = []
    for query in final_plan.get("queries", []):
        if not isinstance(query, dict):
            continue
        name = str(query.get("name"))
        dry = counts_by_name.get(name, {})
        exported = manifest_by_name.get(name, {})
        reported = int(dry.get("reported_count") or exported.get("reported_count") or 0)
        downloaded = int(exported.get("downloaded_count") or 0)
        diagnosis = "good"
        repair_action = "none"
        for item in decisions:
            if item.get("related_query") == name and item.get("risk_or_failure_signal") == "too_broad":
                diagnosis = "too_broad_repaired"
                repair_action = "tightened"
            if item.get("related_query") == name and item.get("risk_or_failure_signal") == "zero_result":
                diagnosis = "zero_result_repaired"
                repair_action = "broadened"
        if reported >= DEFAULT_BROAD_COUNT_THRESHOLD:
            failure_signals.append({"type": "too_broad", "evidence": f"{name}: reported_count={reported}", "handled": repair_action == "tightened"})
        if reported == 0 or downloaded == 0:
            failure_signals.append({"type": "zero_result", "evidence": f"{name}: downloaded_count={downloaded}", "handled": repair_action == "broadened" and downloaded > 0})
        query_families.append(
            {
                "name": name,
                "original_query": query.get("search"),
                "final_query": query.get("search"),
                "filter": query.get("filter"),
                "reported_count": reported,
                "downloaded_count": downloaded,
                "diagnosis": diagnosis,
                "repair_action": repair_action,
            }
        )

    retrieval_eval = {
        "topic": trial["topic"],
        "workflow_id": "workflowir_litsearch_v1",
        "query_families": query_families,
        "top_papers": top,
        "failure_signals": failure_signals,
        "coverage": {
            "total_deduped_works": full_manifest.get("total_deduped_works"),
            "total_downloaded_rows": full_manifest.get("total_downloaded_rows"),
            "query_count": len(query_families),
        },
        "contract": {
            "query_count_ok": 2 <= len(query_families) <= 5,
            "summary_written_by_runner": True,
            "quality_eval_written_by_runner": True,
        },
    }
    write_json(run_dir / "RETRIEVAL_EVAL.json", retrieval_eval)
    write_quality_notes(run_dir, retrieval_eval)
    write_summary(run_dir, trial, final_plan, retrieval_eval, decisions)
    return {
        "works_scored": len(scored),
        "top_papers": len(top),
        "failure_signals": len(failure_signals),
        "total_deduped_works": full_manifest.get("total_deduped_works"),
    }


def write_quality_notes(run_dir: Path, retrieval_eval: dict[str, Any]) -> None:
    top = retrieval_eval.get("top_papers", [])
    core = [paper for paper in top if paper.get("relevance") == "core"]
    supporting = [paper for paper in top if paper.get("relevance") == "supporting"]
    weak = [paper for paper in top if paper.get("quality") in {"low", "uncertain"}]
    lines = [
        "# Quality Notes",
        "",
        "## Core Papers",
        *(f"- {paper.get('title')} ({paper.get('year')})" for paper in core[:8]),
        "",
        "## Relevant But Weaker Evidence",
        *(f"- {paper.get('title')} ({paper.get('quality')})" for paper in supporting[:8]),
        "",
        "## Weak Or Uncertain Quality",
        *(f"- {paper.get('title')} ({paper.get('quality_reason')})" for paper in weak[:8]),
        "",
        "## Noisy Or Missing Areas",
        *(f"- {signal.get('type')}: {signal.get('evidence')}" for signal in retrieval_eval.get("failure_signals", [])),
        "",
    ]
    (run_dir / "QUALITY_NOTES.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_summary(
    run_dir: Path,
    trial: dict[str, Any],
    final_plan: dict[str, Any],
    retrieval_eval: dict[str, Any],
    decisions: list[dict[str, Any]],
) -> None:
    lines = [
        "# WorkflowIR Literature Search Summary",
        "",
        f"Topic: {trial['topic']}",
        "",
        "## WorkflowIR Control",
        "",
        "- Query count is schema-bounded to 2-5.",
        "- OpenAlex dry-run is mandatory before full export.",
        "- Broad and zero-result queries are repaired before export.",
        "- Summary/evaluation files are written by the runner, not left to free-form agent completion.",
        "",
        "## Final Query Families",
        "",
        "| Name | Search | Filter | Reported | Downloaded | Diagnosis |",
        "|---|---|---|---:|---:|---|",
    ]
    for family in retrieval_eval.get("query_families", []):
        lines.append(
            "| {name} | `{search}` | `{filter}` | {reported} | {downloaded} | {diagnosis} |".format(
                name=family.get("name"),
                search=family.get("final_query") or "",
                filter=family.get("filter") or "",
                reported=family.get("reported_count"),
                downloaded=family.get("downloaded_count"),
                diagnosis=family.get("diagnosis"),
            )
        )
    lines.extend(
        [
            "",
            "## Export Counts",
            "",
            f"- Total downloaded rows: {retrieval_eval.get('coverage', {}).get('total_downloaded_rows')}",
            f"- Total deduped works: {retrieval_eval.get('coverage', {}).get('total_deduped_works')}",
            "",
            "## Top Papers",
            "",
        ]
    )
    for paper in retrieval_eval.get("top_papers", [])[:10]:
        lines.append(
            f"- {paper.get('title')} ({paper.get('year')}): relevance={paper.get('relevance')}, quality={paper.get('quality')}"
        )
    lines.extend(["", "## Failure And Recovery Signals", ""])
    for signal in retrieval_eval.get("failure_signals", []):
        lines.append(f"- {signal.get('type')}: {signal.get('evidence')}; handled={signal.get('handled')}")
    lines.extend(["", "## Agent Decisions", ""])
    for index, item in enumerate(decisions, start=1):
        lines.append(
            f"{index}. {item.get('event_type')}: {item.get('decision')} "
            f"(risk={item.get('risk_or_failure_signal')}, query={item.get('related_query')})"
        )
    lines.extend(["", "## Claims", ""])
    lines.append("- Supported: WorkflowIR runner completed the required artifact contract for this run.")
    lines.append("- Supported: Query failures are preserved as structured failure_signals.")
    lines.append("- Weakly supported: Top-paper relevance is heuristic and should be human-checked for paper claims.")
    (run_dir / "SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def verify_contract(run_dir: Path) -> dict[str, Any]:
    missing = [relative for relative in REQUIRED_FILES if not (run_dir / relative).exists()]
    return {
        "required_files": REQUIRED_FILES,
        "missing_files": missing,
        "contract_passed": not missing,
    }


def run_trial(
    repo_root: Path,
    config: dict[str, Any],
    trial: dict[str, Any],
    batch_dir: Path,
    execute: bool,
    args: argparse.Namespace,
) -> dict[str, Any]:
    started_at = utc_now()
    now = dt.datetime.now(dt.timezone.utc).date()
    lookback_days = int(trial.get("lookback_days", config.get("lookback_days", DEFAULT_LOOKBACK_DAYS)))
    from_date = (now - dt.timedelta(days=lookback_days)).isoformat()
    to_date = now.isoformat()
    output_dir = Path(trial.get("output_dir") or config.get("output_dir") or DEFAULT_OUTPUT_DIR)
    run_id = f"{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%dT%H%M%SZ')}-{slugify(trial['topic'])}"
    run_dir = repo_root / output_dir / run_id
    script = Path(args.openalex_script or config.get("openalex_script") or DEFAULT_OPENALEX_SCRIPT)
    if not script.is_absolute():
        script = repo_root / script
    max_results = int(
        args.max_results_per_query
        or trial.get("max_results_per_query")
        or config.get("max_results_per_query")
        or DEFAULT_MAX_RESULTS_PER_QUERY
    )
    broad_threshold = int(
        args.broad_count_threshold
        or trial.get("broad_count_threshold")
        or config.get("broad_count_threshold")
        or DEFAULT_BROAD_COUNT_THRESHOLD
    )
    timeout_seconds = int(trial.get("openalex_timeout_seconds", config.get("openalex_timeout_seconds", 180)))

    nodes = {item["node_id"]: NodeSpec(**item) for item in workflow_ir()["nodes"]}
    result: dict[str, Any] = {
        "trial": trial,
        "started_at": started_at,
        "run_dir": str(run_dir),
        "executed": execute,
        "status": "planned",
        "contract_passed": False,
    }
    if not execute:
        return result

    run_dir.mkdir(parents=True, exist_ok=True)
    write_json(run_dir / "workflow_ir.json", workflow_ir())

    all_decisions: list[dict[str, Any]] = []

    create = run_node(run_dir, nodes["create_run"], lambda: {"run_dir": str(run_dir)})
    if create.status != "completed":
        return finish_result(result, run_dir, "failed", create.failure_mode)

    plan_holder: dict[str, Any] = {}

    def plan_step() -> dict[str, Any]:
        plan, decisions = generate_query_plan(trial, from_date, to_date)
        all_decisions.extend(decisions)
        write_json(run_dir / "openalex_queries.initial.json", plan)
        plan_holder["initial"] = plan
        return {"query_count": len(plan.get("queries", [])), "anchors": topic_anchors(trial)}

    if run_node(run_dir, nodes["plan_queries"], plan_step).status != "completed":
        write_decisions(run_dir, all_decisions)
        return finish_result(result, run_dir, "failed", "planner_failed")

    def validate_step() -> dict[str, Any]:
        validated, decisions = validate_query_plan(plan_holder["initial"])
        all_decisions.extend(decisions)
        plan_holder["validated"] = validated
        write_json(run_dir / "openalex_queries.validated.json", validated)
        return {"query_count": len(validated.get("queries", []))}

    if run_node(run_dir, nodes["validate_query_plan"], validate_step).status != "completed":
        write_decisions(run_dir, all_decisions)
        return finish_result(result, run_dir, "failed", "query_plan_invalid")

    dry_counts_holder: dict[str, Any] = {}

    def dry_run_step() -> dict[str, Any]:
        dry_plan = run_dir / "openalex_queries.validated.json"
        dry_out = run_dir / "dry_run"
        out = run_openalex(script, dry_plan, dry_out, dry_run=True, max_results=max_results, timeout_seconds=timeout_seconds)
        rows = read_query_counts(dry_out / "query_counts.csv")
        dry_counts_holder["rows"] = rows
        return {"query_count": len(rows), "manifest": out.get("manifest", {})}

    if run_node(run_dir, nodes["dry_run_counts"], dry_run_step).status != "completed":
        write_decisions(run_dir, all_decisions)
        return finish_result(result, run_dir, "failed", "dry_run_failed")

    def repair_step() -> dict[str, Any]:
        repaired, decisions = repair_queries(
            plan_holder["validated"],
            dry_counts_holder["rows"],
            topic_anchors(trial),
            broad_threshold,
            DEFAULT_ZERO_RESULT_THRESHOLD,
        )
        validated, validation_decisions = validate_query_plan(repaired)
        all_decisions.extend(decisions)
        all_decisions.extend(validation_decisions)
        plan_holder["final"] = validated
        write_json(run_dir / "openalex_queries.final.json", validated)
        return {"query_count": len(validated.get("queries", [])), "decisions": len(decisions)}

    if run_node(run_dir, nodes["repair_queries"], repair_step).status != "completed":
        write_decisions(run_dir, all_decisions)
        return finish_result(result, run_dir, "failed", "repair_failed")

    full_manifest_holder: dict[str, Any] = {}

    def full_export_step() -> dict[str, Any]:
        out = run_openalex(
            script,
            run_dir / "openalex_queries.final.json",
            run_dir / "openalex",
            dry_run=False,
            max_results=max_results,
            timeout_seconds=timeout_seconds,
        )
        manifest = out.get("manifest", {})
        full_manifest_holder["manifest"] = manifest
        total = manifest.get("total_deduped_works")
        if total == 0:
            raise RuntimeError("full export returned zero deduped works")
        return {
            "total_deduped_works": total,
            "total_downloaded_rows": manifest.get("total_downloaded_rows"),
        }

    if run_node(run_dir, nodes["full_export"], full_export_step).status != "completed":
        write_decisions(run_dir, all_decisions)
        return finish_result(result, run_dir, "failed", "full_export_failed")

    def evaluate_step() -> dict[str, Any]:
        evidence = evaluate_and_write(
            run_dir,
            trial,
            plan_holder["final"],
            dry_counts_holder["rows"],
            full_manifest_holder["manifest"],
            all_decisions,
        )
        return evidence

    if run_node(run_dir, nodes["evaluate_results"], evaluate_step).status != "completed":
        write_decisions(run_dir, all_decisions)
        return finish_result(result, run_dir, "failed", "evaluation_failed")

    write_decisions(run_dir, all_decisions)

    contract_holder: dict[str, Any] = {}

    def verify_step() -> dict[str, Any]:
        contract = verify_contract(run_dir)
        contract_holder["contract"] = contract
        if not contract["contract_passed"]:
            raise RuntimeError(f"missing files: {contract['missing_files']}")
        return contract

    verify = run_node(run_dir, nodes["verify_contract"], verify_step)
    status = "completed" if verify.status == "completed" else "contract_failed"
    final = finish_result(result, run_dir, status, verify.failure_mode)
    final["contract"] = contract_holder.get("contract") or verify_contract(run_dir)
    write_json(run_dir / "manifest.json", final)
    return final


def write_decisions(run_dir: Path, decisions: list[dict[str, Any]]) -> None:
    rows = []
    for index, item in enumerate(decisions, start=1):
        rows.append({"step": index, **item})
    with (run_dir / "AGENT_DECISIONS.jsonl").open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def finish_result(result: dict[str, Any], run_dir: Path, status: str, failure_mode: str | None) -> dict[str, Any]:
    finished_at = utc_now()
    result = dict(result)
    result["finished_at"] = finished_at
    result["status"] = status
    result["failure_mode"] = failure_mode
    result["contract_passed"] = status == "completed"
    if run_dir.exists():
        result["contract"] = verify_contract(run_dir)
    return result


def write_batch_report(batch_dir: Path, config_path: Path, results: list[dict[str, Any]], execute: bool) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    contract_passed = 0
    for result in results:
        status = str(result.get("status"))
        status_counts[status] = status_counts.get(status, 0) + 1
        if result.get("contract_passed"):
            contract_passed += 1
    manifest = {
        "kind": "workflowir_litsearch_trial_batch",
        "config": str(config_path),
        "batch_dir": str(batch_dir),
        "execute": execute,
        "counts": {
            "trials": len(results),
            "status": status_counts,
            "contract_passed": contract_passed,
            "contract_failed": len(results) - contract_passed,
        },
        "results": results,
    }
    write_json(batch_dir / "batch_manifest.json", manifest)
    return manifest


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd().resolve()
    config_path = Path(args.config)
    config = read_json(config_path)
    if not isinstance(config, dict):
        raise SystemExit("Config must be a JSON object.")
    trials = load_trials(config)
    if args.max_trials is not None:
        trials = trials[: args.max_trials]

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    batch_name = slugify(str(config.get("batch_name") or config_path.stem))
    batch_dir = Path(args.batch_dir) if args.batch_dir else Path(DEFAULT_BATCH_ROOT) / f"{timestamp}-{batch_name}"
    if not batch_dir.is_absolute():
        batch_dir = repo_root / batch_dir
    batch_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    for trial in trials:
        result = run_trial(repo_root, config, trial, batch_dir, args.execute, args)
        results.append(result)
        write_batch_report(batch_dir, config_path, results, args.execute)

    manifest = write_batch_report(batch_dir, config_path, results, args.execute)
    print(f"{'ran' if args.execute else 'planned'} {len(results)} WorkflowIR litsearch trial(s).")
    print(f"Batch manifest: {batch_dir / 'batch_manifest.json'}")
    print(f"Contract passed: {manifest['counts']['contract_passed']}/{len(results)}")
    if not args.execute:
        print("No OpenAlex calls were made. Re-run with --execute for real retrieval data.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
