#!/usr/bin/env python3
"""Run real AI-agent literature-watch trials and build a trace dataset.

This script is the automated data-generation loop for real failures:

1. read a batch of real literature-search trial topics;
2. invoke the ARIS literature-watch runner for each trial;
3. keep successful, blocked, and failed runs as data;
4. rebuild the real trace dataset from the generated run artifacts.

It intentionally does not synthesize task answers. The data comes from actual
agent calls, real OpenAlex calls, and whatever mistakes or recovery behavior the
agent produces during execution.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any


DEFAULT_CONFIG = "configs/real_litwatch_trials.example.json"


def read_json(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SystemExit(f"Config must be a JSON object: {path}")
    return payload


def read_text_if_present(path: Path | None) -> str | None:
    if path is None:
        return None
    try:
        text = path.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise SystemExit(f"Prompt contract file not found: {path}")
    return text or None


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def slugify(value: str, max_length: int = 96) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if len(value) > max_length:
        value = value[:max_length].rstrip("-._")
    return value or "trial"


def list_trials(config: dict[str, Any]) -> list[dict[str, Any]]:
    trials = config.get("trials")
    if not isinstance(trials, list) or not trials:
        raise SystemExit("Config must contain a non-empty trials array.")
    normalized: list[dict[str, Any]] = []
    for index, trial in enumerate(trials, start=1):
        if not isinstance(trial, dict):
            raise SystemExit(f"Trial #{index} must be an object.")
        topic = str(trial.get("topic", "")).strip()
        if not topic:
            raise SystemExit(f"Trial #{index} is missing topic.")
        name = str(trial.get("name") or slugify(topic)).strip()
        normalized.append({**trial, "name": slugify(name), "topic": topic})
    return normalized


def optional_arg(command: list[str], flag: str, value: Any) -> None:
    if value is not None and value != "":
        command.extend([flag, str(value)])


def bool_arg(command: list[str], flag: str, value: Any) -> None:
    if bool(value):
        command.append(flag)


def build_trial_command(
    repo_root: Path,
    config: dict[str, Any],
    trial: dict[str, Any],
    batch_dir: Path,
) -> tuple[list[str], Path | None]:
    runner_script = repo_root / "scripts" / "aris_openalex_lit_watch.py"
    command = [sys.executable, str(runner_script)]
    output_dir = Path(trial.get("output_dir") or config.get("output_dir") or "lit-watch/real-agent-trials")
    project = trial["name"]

    reviewer_direction_path = None
    reviewer_direction = trial.get("reviewer_direction") or trial.get("reviewer_direction_text")
    if isinstance(reviewer_direction, str) and reviewer_direction.strip():
        reviewer_direction_path = batch_dir / "reviewer_directions" / f"{project}.md"
        reviewer_direction_path.parent.mkdir(parents=True, exist_ok=True)
        reviewer_direction_path.write_text(reviewer_direction.strip() + "\n", encoding="utf-8")

    optional_arg(command, "--project", project)
    optional_arg(command, "--topic", trial["topic"])
    optional_arg(command, "--output-dir", output_dir)
    optional_arg(command, "--wiki-dir", trial.get("wiki_dir", config.get("wiki_dir")))
    optional_arg(command, "--openalex-skill-dir", trial.get("openalex_skill_dir", config.get("openalex_skill_dir")))
    optional_arg(command, "--aris-bin", trial.get("aris_bin", config.get("aris_bin")))
    optional_arg(command, "--model", trial.get("model", config.get("model")))
    optional_arg(command, "--permission-mode", trial.get("permission_mode", config.get("permission_mode")))
    optional_arg(command, "--lookback-days", trial.get("lookback_days", config.get("lookback_days")))
    optional_arg(
        command,
        "--max-results-per-query",
        trial.get("max_results_per_query", config.get("max_results_per_query")),
    )
    optional_arg(command, "--allowed-tools", trial.get("allowed_tools", config.get("allowed_tools")))
    optional_arg(
        command,
        "--extra-instruction",
        combine_extra_instruction(
            prompt_contract_text(repo_root, config, trial),
            config.get("extra_instruction"),
            trial.get("extra_instruction"),
        ),
    )
    optional_arg(command, "--reviewer-direction-file", reviewer_direction_path)
    bool_arg(command, "--dry-run-only", trial.get("dry_run_only", config.get("dry_run_only", False)))
    return command, reviewer_direction_path


def prompt_contract_text(repo_root: Path, config: dict[str, Any], trial: dict[str, Any]) -> str | None:
    raw = trial.get("prompt_contract_file", config.get("prompt_contract_file"))
    if not isinstance(raw, str) or not raw.strip():
        return None
    path = Path(raw).expanduser()
    if not path.is_absolute():
        path = repo_root / path
    return read_text_if_present(path)


def combine_extra_instruction(*values: Any) -> str | None:
    parts = [str(value).strip() for value in values if isinstance(value, str) and value.strip()]
    if not parts:
        return None
    return "\n\n".join(parts)


def positive_int_or_none(value: Any) -> int | None:
    if value is None or value == "":
        return None
    parsed = int(value)
    return parsed if parsed > 0 else None


def run_command_with_timeout(
    command: list[str],
    cwd: Path,
    timeout_seconds: int | None,
) -> tuple[str, str, int, bool]:
    process = subprocess.Popen(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        start_new_session=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout_seconds)
        return stdout or "", stderr or "", int(process.returncode or 0), False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            stdout, stderr = process.communicate(timeout=10)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            stdout, stderr = process.communicate()
        stderr = (stderr or "") + f"\n[TIMEOUT] Trial exceeded {timeout_seconds} seconds.\n"
        return stdout or "", stderr, int(process.returncode or -1), True


def run_trial(
    repo_root: Path,
    config: dict[str, Any],
    trial: dict[str, Any],
    batch_dir: Path,
    execute: bool,
) -> dict[str, Any]:
    command, reviewer_direction_path = build_trial_command(repo_root, config, trial, batch_dir)
    started_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    log_dir = batch_dir / "trial_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    stdout_path = log_dir / f"{trial['name']}.stdout.txt"
    stderr_path = log_dir / f"{trial['name']}.stderr.txt"
    command_display = command[:]
    timeout_seconds = positive_int_or_none(trial.get("trial_timeout_seconds", config.get("trial_timeout_seconds")))

    result: dict[str, Any] = {
        "trial": trial,
        "started_at": started_at,
        "command": command_display,
        "reviewer_direction_file": str(reviewer_direction_path) if reviewer_direction_path else None,
        "stdout_log": str(stdout_path),
        "stderr_log": str(stderr_path),
        "executed": execute,
        "returncode": None,
        "status": "planned",
        "timeout_seconds": timeout_seconds,
    }
    if not execute:
        return result

    stdout, stderr, returncode, timed_out = run_command_with_timeout(command, repo_root, timeout_seconds)
    stdout_path.write_text(stdout, encoding="utf-8")
    stderr_path.write_text(stderr, encoding="utf-8")
    result["returncode"] = returncode
    result["timed_out"] = timed_out
    result["status"] = "timeout" if timed_out else ("completed" if returncode == 0 else "failed_or_blocked")
    result["finished_at"] = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    result["run_directory_hint"] = extract_run_dir(stdout + "\n" + stderr)
    return result


def extract_run_dir(text: str) -> str | None:
    for pattern in [r"Run directory:\s*(.+)", r"Run directory:\s*`([^`]+)`"]:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def rebuild_trace_dataset(repo_root: Path, config: dict[str, Any], batch_manifest: dict[str, Any], execute: bool) -> dict[str, Any] | None:
    if not execute or not bool(config.get("rebuild_trace_dataset", True)):
        return None
    runs_dir = Path(config.get("output_dir") or "lit-watch/real-agent-trials")
    trace_out_dir = Path(config.get("trace_out_dir") or "data/real_agent_litwatch_traces/latest")
    command = [
        sys.executable,
        str(repo_root / "scripts" / "build_real_litwatch_trace_dataset.py"),
        "--runs-dir",
        str(runs_dir),
        "--out-dir",
        str(trace_out_dir),
        "--batch-dir",
        str(batch_manifest["batch_dir"]),
    ]
    completed = subprocess.run(command, cwd=repo_root, text=True, capture_output=True, check=False)
    trace_log_dir = Path(batch_manifest["batch_dir"]) / "trace_builder"
    trace_log_dir.mkdir(parents=True, exist_ok=True)
    (trace_log_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (trace_log_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    return {
        "command": command,
        "returncode": completed.returncode,
        "stdout_log": str(trace_log_dir / "stdout.txt"),
        "stderr_log": str(trace_log_dir / "stderr.txt"),
        "trace_out_dir": str(trace_out_dir),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--max-trials", type=int, default=None, help="Limit the number of trials from the config.")
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually call ARIS/AI/OpenAlex. Without this flag, only write a batch plan.",
    )
    parser.add_argument(
        "--batch-dir",
        default=None,
        help="Directory for batch logs and manifest. Defaults to lit-watch/trial-batches/<timestamp>.",
    )
    parser.add_argument(
        "--trial-timeout-seconds",
        type=int,
        default=None,
        help="Maximum seconds per real ARIS trial before recording timeout and continuing.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    repo_root = Path.cwd().resolve()
    config_path = Path(args.config)
    config = read_json(config_path)
    if args.trial_timeout_seconds is not None:
        config["trial_timeout_seconds"] = args.trial_timeout_seconds
    trials = list_trials(config)
    if args.max_trials is not None:
        trials = trials[: args.max_trials]

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    batch_name = slugify(str(config.get("batch_name") or config_path.stem))
    batch_dir = Path(args.batch_dir) if args.batch_dir else Path("lit-watch") / "trial-batches" / f"{timestamp}-{batch_name}"
    batch_dir.mkdir(parents=True, exist_ok=True)

    results: list[dict[str, Any]] = []
    continue_on_error = bool(config.get("continue_on_error", True))
    for trial in trials:
        result = run_trial(repo_root, config, trial, batch_dir, execute=args.execute)
        results.append(result)
        write_json(batch_dir / "batch_manifest.json", provisional_manifest(config_path, batch_dir, results, args.execute))
        if args.execute and result["returncode"] not in (0, None) and not continue_on_error:
            break

    manifest = provisional_manifest(config_path, batch_dir, results, args.execute)
    trace_result = rebuild_trace_dataset(repo_root, config, manifest, execute=args.execute)
    manifest["trace_dataset_build"] = trace_result
    write_json(batch_dir / "batch_manifest.json", manifest)

    planned_or_ran = "ran" if args.execute else "planned"
    print(f"{planned_or_ran} {len(results)} real lit-watch trial(s).")
    print(f"Batch manifest: {batch_dir / 'batch_manifest.json'}")
    if trace_result:
        print(f"Trace dataset: {trace_result['trace_out_dir']}")
    if not args.execute:
        print("No AI/API calls were made. Re-run with --execute to generate real agent-call data.")
    return 0


def provisional_manifest(config_path: Path, batch_dir: Path, results: list[dict[str, Any]], execute: bool) -> dict[str, Any]:
    status_counts: dict[str, int] = {}
    for result in results:
        status = str(result.get("status"))
        status_counts[status] = status_counts.get(status, 0) + 1
    return {
        "kind": "real_litwatch_trial_batch",
        "config": str(config_path),
        "batch_dir": str(batch_dir),
        "execute": execute,
        "counts": {
            "trials": len(results),
            "status": status_counts,
        },
        "results": results,
    }


if __name__ == "__main__":
    raise SystemExit(main())
