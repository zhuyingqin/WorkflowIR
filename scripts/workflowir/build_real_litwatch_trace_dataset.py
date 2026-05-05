#!/usr/bin/env python3
"""Build a real agent-run trace dataset from existing lit-watch runs.

It mines artifacts already produced by ARIS/Codex literature-watch runs:
prompts, reviewer directions, OpenAlex query plans, OpenAlex export manifests,
summaries, stdout, stderr, and BLOCKED records. The output is a reproducible
trace dataset of real agent behavior and observed run anomalies.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
import datetime as dt
import json
import re
from pathlib import Path
from typing import Any


DATASET_ID = "real_agent_litwatch_traces_v1"
DATASET_VERSION = "0.1.0"
DEFAULT_RUNS_DIR = "lit-watch/runs"
DEFAULT_OUT_DIR = "data/real_agent_litwatch_traces/v1"


def read_text(path: Path, limit: int | None = None) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    if limit is not None and len(text) > limit:
        return text[:limit]
    return text


def read_json(path: Path) -> Any | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        return None


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False, sort_keys=False) + "\n")


def discover_runs(runs_dir: Path) -> list[Path]:
    if not runs_dir.exists():
        return []
    return sorted(path for path in runs_dir.iterdir() if path.is_dir() and not path.name.startswith("."))


def parse_run_timestamp(run_id: str) -> str | None:
    match = re.match(r"^(\d{8}T\d{6}Z)-", run_id)
    if not match:
        return None
    try:
        return dt.datetime.strptime(match.group(1), "%Y%m%dT%H%M%SZ").replace(tzinfo=dt.timezone.utc).isoformat()
    except ValueError:
        return None


def parse_iso_timestamp(value: Any) -> dt.datetime | None:
    if not isinstance(value, str) or not value.strip():
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def load_runner_statuses(batch_dir: Path | None, runs_dir: Path, repo_root: Path) -> dict[str, dict[str, Any]]:
    if batch_dir is None:
        return {}
    batch_manifest_path = batch_dir / "batch_manifest.json"
    batch_manifest = read_json(batch_manifest_path)
    if not isinstance(batch_manifest, dict):
        return {}

    runs_by_project: dict[str, list[tuple[dt.datetime | None, Path]]] = defaultdict(list)
    for run_dir in discover_runs(runs_dir):
        watch_manifest = read_json(run_dir / "watch_manifest.json")
        if not isinstance(watch_manifest, dict):
            continue
        settings = watch_manifest.get("settings")
        if not isinstance(settings, dict):
            continue
        project = settings.get("project")
        if not isinstance(project, str) or not project:
            continue
        started = parse_iso_timestamp(watch_manifest.get("started_at")) or parse_iso_timestamp(parse_run_timestamp(run_dir.name))
        runs_by_project[project].append((started, run_dir))

    statuses: dict[str, dict[str, Any]] = {}
    for result in batch_manifest.get("results", []):
        if not isinstance(result, dict):
            continue
        trial = result.get("trial")
        if not isinstance(trial, dict):
            continue
        run_dir = resolve_result_run_dir(result, trial, runs_by_project)
        if run_dir is None:
            continue
        statuses[run_dir.name] = {
            "status": result.get("status"),
            "returncode": result.get("returncode"),
            "timed_out": result.get("timed_out"),
            "timeout_seconds": result.get("timeout_seconds"),
            "started_at": result.get("started_at"),
            "finished_at": result.get("finished_at"),
            "batch_manifest": relpath(batch_manifest_path, repo_root),
            "stdout_log": result.get("stdout_log"),
            "stderr_log": result.get("stderr_log"),
        }
    return statuses


def resolve_result_run_dir(
    result: dict[str, Any],
    trial: dict[str, Any],
    runs_by_project: dict[str, list[tuple[dt.datetime | None, Path]]],
) -> Path | None:
    hint = result.get("run_directory_hint")
    if isinstance(hint, str) and hint.strip():
        hinted = Path(hint)
        if hinted.exists():
            return hinted

    project = trial.get("name")
    if not isinstance(project, str) or not project:
        return None
    candidates = runs_by_project.get(project, [])
    if not candidates:
        return None

    started_at = parse_iso_timestamp(result.get("started_at"))
    finished_at = parse_iso_timestamp(result.get("finished_at"))
    windowed: list[tuple[dt.datetime | None, Path]] = []
    for started, run_dir in candidates:
        if started_at and started and started < started_at - dt.timedelta(seconds=90):
            continue
        if finished_at and started and started > finished_at + dt.timedelta(seconds=90):
            continue
        windowed.append((started, run_dir))
    if not windowed:
        windowed = candidates

    def distance(item: tuple[dt.datetime | None, Path]) -> float:
        started, _ = item
        if started_at and started:
            return abs((started - started_at).total_seconds())
        return float("inf")

    return min(windowed, key=distance)[1]


def compact_query_plan(query_plan: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(query_plan, dict):
        return {"exists": False, "query_count": 0, "queries": []}
    queries = query_plan.get("queries")
    if not isinstance(queries, list):
        queries = []
    return {
        "exists": True,
        "project": query_plan.get("project"),
        "description": query_plan.get("description"),
        "shared_filter": (query_plan.get("shared") or {}).get("filter") if isinstance(query_plan.get("shared"), dict) else None,
        "query_count": len(queries),
        "queries": [
            {
                "index": index,
                "name": query.get("name"),
                "search": query.get("search") or query.get("title_and_abstract.search"),
            }
            for index, query in enumerate(queries, start=1)
            if isinstance(query, dict)
        ],
    }


def compact_openalex_manifest(manifest: dict[str, Any] | None) -> dict[str, Any]:
    if not isinstance(manifest, dict):
        return {"exists": False, "query_count": 0, "total_deduped_works": None, "total_downloaded_rows": None}
    queries = manifest.get("queries") if isinstance(manifest.get("queries"), list) else []
    return {
        "exists": True,
        "dry_run": manifest.get("dry_run"),
        "started_at": manifest.get("started_at"),
        "finished_at": manifest.get("finished_at"),
        "endpoint": manifest.get("endpoint"),
        "query_count": len(queries),
        "total_deduped_works": manifest.get("total_deduped_works"),
        "total_downloaded_rows": manifest.get("total_downloaded_rows"),
        "queries": [
            {
                "index": query.get("index", index),
                "name": query.get("name"),
                "reported_count": query.get("reported_count"),
                "downloaded_count": query.get("downloaded_count"),
                "pages_downloaded": query.get("pages_downloaded"),
                "search": ((query.get("params") or {}).get("search") if isinstance(query.get("params"), dict) else None),
                "filter": ((query.get("params") or {}).get("filter") if isinstance(query.get("params"), dict) else None),
            }
            for index, query in enumerate(queries, start=1)
            if isinstance(query, dict)
        ],
    }


def classify_status(run_dir: Path, openalex_manifest: dict[str, Any], summary_text: str) -> str:
    has_blocked = (run_dir / "BLOCKED.md").exists()
    has_summary = bool(summary_text.strip())
    has_export = bool(openalex_manifest.get("exists"))
    if has_blocked and not has_export:
        return "blocked"
    if has_blocked and has_export:
        return "completed_with_blocked_note"
    if has_summary and has_export:
        return "completed"
    if has_export:
        return "exported_without_summary"
    if has_summary:
        return "summary_without_export"
    return "incomplete"


def make_trace(run_dir: Path, repo_root: Path, runner_statuses: dict[str, dict[str, Any]]) -> dict[str, Any]:
    run_id = run_dir.name
    query_plan_raw = read_json(run_dir / "openalex_queries.json")
    openalex_manifest_raw = read_json(run_dir / "openalex" / "manifest.json")
    watch_manifest = read_json(run_dir / "watch_manifest.json")
    prompt_text = read_text(run_dir / "prompt.md")
    reviewer_text = read_text(run_dir / "reviewer_direction.md")
    summary_text = read_text(run_dir / "SUMMARY.md")
    blocked_text = read_text(run_dir / "BLOCKED.md")
    stdout_text = read_text(run_dir / "aris.stdout.txt", limit=20_000)
    stderr_text = read_text(run_dir / "aris.stderr.txt", limit=20_000)

    query_plan = compact_query_plan(query_plan_raw)
    openalex_manifest = compact_openalex_manifest(openalex_manifest_raw)
    artifact_status = classify_status(run_dir, openalex_manifest, summary_text)
    runner_status = runner_statuses.get(run_id)
    status = "timeout" if isinstance(runner_status, dict) and runner_status.get("timed_out") else artifact_status
    output_files = {
        "prompt": relpath(run_dir / "prompt.md", repo_root) if (run_dir / "prompt.md").exists() else None,
        "reviewer_direction": relpath(run_dir / "reviewer_direction.md", repo_root)
        if (run_dir / "reviewer_direction.md").exists()
        else None,
        "query_plan": relpath(run_dir / "openalex_queries.json", repo_root)
        if (run_dir / "openalex_queries.json").exists()
        else None,
        "openalex_manifest": relpath(run_dir / "openalex" / "manifest.json", repo_root)
        if (run_dir / "openalex" / "manifest.json").exists()
        else None,
        "deduped_results": relpath(run_dir / "openalex" / "all_results_deduped.jsonl", repo_root)
        if (run_dir / "openalex" / "all_results_deduped.jsonl").exists()
        else None,
        "summary": relpath(run_dir / "SUMMARY.md", repo_root) if (run_dir / "SUMMARY.md").exists() else None,
        "blocked": relpath(run_dir / "BLOCKED.md", repo_root) if (run_dir / "BLOCKED.md").exists() else None,
        "stdout": relpath(run_dir / "aris.stdout.txt", repo_root) if (run_dir / "aris.stdout.txt").exists() else None,
        "stderr": relpath(run_dir / "aris.stderr.txt", repo_root) if (run_dir / "aris.stderr.txt").exists() else None,
    }

    return {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "run_id": run_id,
        "started_at_from_id": parse_run_timestamp(run_id),
        "status": status,
        "artifact_status": artifact_status,
        "runner_status": runner_status,
        "topic_slug": re.sub(r"^\d{8}T\d{6}Z-", "", run_id),
        "watch_manifest": watch_manifest if isinstance(watch_manifest, dict) else None,
        "artifacts": output_files,
        "query_plan": query_plan,
        "openalex_manifest": openalex_manifest,
        "text_stats": {
            "prompt_chars": len(prompt_text),
            "reviewer_direction_chars": len(reviewer_text),
            "summary_chars": len(summary_text),
            "blocked_chars": len(blocked_text),
            "stdout_chars": len(stdout_text),
            "stderr_chars": len(stderr_text),
        },
    }


def relpath(path: Path, root: Path) -> str:
    try:
        return str(path.resolve().relative_to(root.resolve()))
    except ValueError:
        return str(path)


def event_rows(trace: dict[str, Any]) -> list[dict[str, Any]]:
    run_id = trace["run_id"]
    rows: list[dict[str, Any]] = []
    for event_type, artifact_key in [
        ("agent.prompt_created", "prompt"),
        ("agent.reviewer_direction_created", "reviewer_direction"),
        ("agent.query_plan_created", "query_plan"),
        ("agent.summary_written", "summary"),
        ("agent.blocked_record_written", "blocked"),
    ]:
        path = trace["artifacts"].get(artifact_key)
        if path:
            rows.append(
                {
                    "dataset_id": DATASET_ID,
                    "run_id": run_id,
                    "event_type": event_type,
                    "artifact": path,
                    "status": "observed",
                }
            )
    manifest = trace["openalex_manifest"]
    if manifest.get("exists"):
        rows.append(
            {
                "dataset_id": DATASET_ID,
                "run_id": run_id,
                "event_type": "tool.openalex_export_started",
                "artifact": trace["artifacts"].get("openalex_manifest"),
                "status": "observed",
                "started_at": manifest.get("started_at"),
                "finished_at": manifest.get("finished_at"),
                "total_deduped_works": manifest.get("total_deduped_works"),
                "total_downloaded_rows": manifest.get("total_downloaded_rows"),
            }
        )
        for query in manifest.get("queries", []):
            rows.append(
                {
                    "dataset_id": DATASET_ID,
                    "run_id": run_id,
                    "event_type": "tool.openalex_query",
                    "tool_id": "openalex_works_export",
                    "query_index": query.get("index"),
                    "query_name": query.get("name"),
                    "reported_count": query.get("reported_count"),
                    "downloaded_count": query.get("downloaded_count"),
                    "pages_downloaded": query.get("pages_downloaded"),
                    "search": query.get("search"),
                    "filter": query.get("filter"),
                }
            )
    return rows


def anomaly(
    run_id: str,
    label: str,
    severity: str,
    evidence: str,
    source: str = "automatic_artifact_mining",
) -> dict[str, Any]:
    return {
        "dataset_id": DATASET_ID,
        "run_id": run_id,
        "label": label,
        "severity": severity,
        "evidence": evidence,
        "source": source,
    }


def anomaly_rows(trace: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    run_id = trace["run_id"]
    status = trace["status"]
    query_plan = trace["query_plan"]
    manifest = trace["openalex_manifest"]
    text_stats = trace["text_stats"]
    runner_status = trace.get("runner_status")

    if status == "timeout":
        timeout_seconds = runner_status.get("timeout_seconds") if isinstance(runner_status, dict) else None
        rows.append(anomaly(run_id, "run.timeout", "high", f"timeout_seconds={timeout_seconds}"))
    if status in {"blocked", "incomplete"}:
        rows.append(anomaly(run_id, "run.blocked_or_incomplete", "high", f"status={status}"))
    if status == "completed_with_blocked_note":
        rows.append(anomaly(run_id, "run.completed_with_blocked_note", "medium", "BLOCKED.md exists despite OpenAlex export"))
    if not query_plan.get("exists"):
        rows.append(anomaly(run_id, "agent.missing_query_plan", "high", "openalex_queries.json is missing or invalid"))
    elif not 2 <= int(query_plan.get("query_count", 0)) <= 5:
        rows.append(
            anomaly(
                run_id,
                "agent.query_count_outside_protocol",
                "medium",
                f"query_count={query_plan.get('query_count')}; protocol expects 2-5 query families",
            )
        )
    if not manifest.get("exists"):
        rows.append(anomaly(run_id, "tool.openalex_export_missing", "high", "openalex/manifest.json is missing or invalid"))
    else:
        is_dry_run = bool(manifest.get("dry_run"))
        total_downloaded = manifest.get("total_downloaded_rows")
        total_deduped = manifest.get("total_deduped_works")
        if not is_dry_run and total_deduped == 0:
            rows.append(anomaly(run_id, "tool.openalex_empty_export", "high", "total_deduped_works=0"))
        if isinstance(total_downloaded, int) and isinstance(total_deduped, int) and total_downloaded > 0:
            dedup_ratio = total_deduped / total_downloaded
            if dedup_ratio < 0.7:
                rows.append(
                    anomaly(
                        run_id,
                        "retrieval.high_duplicate_overlap",
                        "low",
                        f"dedup_ratio={dedup_ratio:.3f}; total_downloaded_rows={total_downloaded}; total_deduped_works={total_deduped}",
                    )
                )
        for query in manifest.get("queries", []):
            reported = query.get("reported_count")
            downloaded = query.get("downloaded_count")
            name = query.get("name")
            if reported == 0 or (not is_dry_run and downloaded == 0):
                rows.append(anomaly(run_id, "retrieval.zero_result_query", "medium", f"query={name}; reported={reported}; downloaded={downloaded}"))
            if isinstance(reported, int) and reported >= 300:
                rows.append(anomaly(run_id, "retrieval.query_too_broad", "medium", f"query={name}; reported_count={reported}"))
    if text_stats.get("summary_chars", 0) == 0 and status not in {"blocked", "incomplete"}:
        rows.append(anomaly(run_id, "agent.missing_summary", "medium", "SUMMARY.md is missing after export"))
    return rows


def build_dataset(runs_dir: Path, out_dir: Path, repo_root: Path, batch_dir: Path | None = None) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    runner_statuses = load_runner_statuses(batch_dir, runs_dir, repo_root)
    traces = [make_trace(path, repo_root, runner_statuses) for path in discover_runs(runs_dir)]
    events: list[dict[str, Any]] = []
    anomalies: list[dict[str, Any]] = []
    for trace in traces:
        events.extend(event_rows(trace))
        anomalies.extend(anomaly_rows(trace))

    status_counts: dict[str, int] = {}
    for trace in traces:
        status_counts[trace["status"]] = status_counts.get(trace["status"], 0) + 1
    anomaly_counts: dict[str, int] = {}
    for row in anomalies:
        anomaly_counts[row["label"]] = anomaly_counts.get(row["label"], 0) + 1

    manifest = {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "source": "existing ARIS/Codex lit-watch run artifacts",
        "runs_dir": str(runs_dir),
        "out_dir": str(out_dir),
        "counts": {
            "runs": len(traces),
            "events": len(events),
            "anomalies": len(anomalies),
            "status": dict(sorted(status_counts.items())),
            "anomaly_labels": dict(sorted(anomaly_counts.items())),
        },
        "files": {
            "run_traces": "run_traces.jsonl",
            "tool_events": "tool_events.jsonl",
            "anomalies": "anomalies.jsonl",
            "schema": "schema.json",
            "readme": "README.md",
        },
        "notes": [
            "This dataset is mined from real agent-generated artifacts, not synthetic task templates.",
            "When a batch manifest is provided, runner-level statuses such as timeout are preserved separately from artifact-derived statuses.",
            "It is run-level and artifact-level; finer per-tool LLM traces require instrumenting the agent runtime.",
            "Automatic anomaly labels are weak labels intended for triage, not final human-verified ground truth.",
        ],
    }
    write_jsonl(out_dir / "run_traces.jsonl", traces)
    write_jsonl(out_dir / "tool_events.jsonl", events)
    write_jsonl(out_dir / "anomalies.jsonl", anomalies)
    write_json(out_dir / "manifest.json", manifest)
    write_json(out_dir / "schema.json", schema())
    (out_dir / "README.md").write_text(readme_text(manifest), encoding="utf-8")
    return manifest


def schema() -> dict[str, Any]:
    return {
        "run_trace": {
            "required_fields": [
                "dataset_id",
                "dataset_version",
                "run_id",
                "status",
                "artifact_status",
                "runner_status",
                "artifacts",
                "query_plan",
                "openalex_manifest",
                "text_stats",
            ]
        },
        "tool_event": {
            "event_types": [
                "agent.prompt_created",
                "agent.reviewer_direction_created",
                "agent.query_plan_created",
                "tool.openalex_export_started",
                "tool.openalex_query",
                "agent.summary_written",
                "agent.blocked_record_written",
            ]
        },
        "anomaly": {
            "labels": [
                "run.blocked_or_incomplete",
                "run.completed_with_blocked_note",
                "run.timeout",
                "agent.missing_query_plan",
                "agent.query_count_outside_protocol",
                "agent.missing_summary",
                "tool.openalex_export_missing",
                "tool.openalex_empty_export",
                "retrieval.high_duplicate_overlap",
                "retrieval.zero_result_query",
                "retrieval.query_too_broad",
            ]
        },
    }


def readme_text(manifest: dict[str, Any]) -> str:
    counts = manifest["counts"]
    return f"""# Real Agent Lit-Watch Trace Dataset v1

Dataset id: `{DATASET_ID}`

This dataset is mined from existing ARIS/Codex literature-watch run artifacts.
These rows come from actual agent workflow outputs: prompts, reviewer
directions, OpenAlex query plans, OpenAlex export manifests, summaries, blocked
records, stdout, and stderr when present.

## Scope

- Runs: {counts["runs"]}
- Events: {counts["events"]}
- Automatically detected anomalies: {counts["anomalies"]}

## Files

- `run_traces.jsonl`: one row per real lit-watch run.
- `tool_events.jsonl`: artifact-level event stream and OpenAlex query events.
- `anomalies.jsonl`: weak anomaly labels mined from artifacts.
- `manifest.json`: counts and dataset notes.
- `schema.json`: compact schema summary.

## Important Caveat

This is a real artifact-level trace dataset, not yet a full per-token/per-tool
agent telemetry dataset. To capture exact LLM tool-call arguments, retries, and
exceptions, the next step is to instrument the ARIS/Codex tool runtime and write
JSONL events during live agent execution.
"""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--runs-dir", default=DEFAULT_RUNS_DIR)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR)
    parser.add_argument("--batch-dir", default=None, help="Optional lit-watch trial batch directory with runner statuses.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    repo_root = Path.cwd().resolve()
    manifest = build_dataset(
        Path(args.runs_dir),
        Path(args.out_dir),
        repo_root,
        Path(args.batch_dir) if args.batch_dir else None,
    )
    print(
        f"Built {DATASET_ID}: "
        f"{manifest['counts']['runs']} runs, "
        f"{manifest['counts']['events']} events, "
        f"{manifest['counts']['anomalies']} anomalies"
    )


if __name__ == "__main__":
    main()
