#!/usr/bin/env python3
"""Run one scheduled ARIS/OpenAlex literature watch pass.

The script is intentionally one-shot: use cron, launchd, or another scheduler
to decide when it should wake up. By default ARIS can ask its reviewer model
what direction is missing; when the scheduler is Codex, pass a reviewer
direction file so Codex reviews and ARIS only executes OpenAlex search.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from pathlib import Path
from typing import Any


DEFAULT_LOOKBACK_DAYS = 30
DEFAULT_MAX_RESULTS_PER_QUERY = 300
DEFAULT_PERMISSION_MODE = "danger-full-access"


@dataclass(frozen=True)
class Settings:
    project: str
    topic: str | None
    output_dir: Path
    wiki_dir: Path
    openalex_skill_dir: Path
    aris_bin: str | None
    model: str | None
    permission_mode: str
    lookback_days: int
    max_results_per_query: int
    dry_run_only: bool
    allowed_tools: str | None
    reviewer_direction_file: Path | None
    extra_instruction: str | None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ask ARIS reviewer to choose the next research direction, then run OpenAlex search."
    )
    parser.add_argument("--config", help="Optional JSON config file.")
    parser.add_argument("--project", help="Stable project label for run metadata.")
    parser.add_argument("--topic", help="Optional topic anchor. If omitted, ARIS infers from research-wiki.")
    parser.add_argument("--output-dir", help="Directory for scheduled run outputs.")
    parser.add_argument("--wiki-dir", help="Research wiki directory.")
    parser.add_argument("--openalex-skill-dir", help="Path to the openalex-search skill directory.")
    parser.add_argument("--aris-bin", help="Path to an aris binary. Defaults to target/debug/aris or cargo run.")
    parser.add_argument("--model", help="Optional ARIS executor model override.")
    parser.add_argument("--permission-mode", help="ARIS permission mode.")
    parser.add_argument("--lookback-days", type=int, help="Default freshness window for new papers.")
    parser.add_argument("--max-results-per-query", type=int, help="Cap per OpenAlex query. Use 0 for full export.")
    parser.add_argument("--dry-run-only", action="store_true", help="Only ask ARIS to run OpenAlex dry-run counts.")
    parser.add_argument("--allowed-tools", help="Optional --allowedTools value passed to ARIS.")
    parser.add_argument(
        "--reviewer-direction-file",
        help="Markdown file containing a Codex-produced reviewer direction. When set, ARIS skips LlmReview.",
    )
    parser.add_argument("--extra-instruction", help="Extra instruction appended to the ARIS prompt.")
    parser.add_argument("--print-prompt", action="store_true", help="Write prompt and print it without invoking ARIS.")
    return parser.parse_args()


def load_config(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    with Path(path).expanduser().open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    if not isinstance(payload, dict):
        raise SystemExit("Config file must be a JSON object.")
    return payload


def cfg_value(args: argparse.Namespace, config: dict[str, Any], name: str, default: Any) -> Any:
    value = getattr(args, name)
    if value is not None:
        return value
    return config.get(name, default)


def make_settings(args: argparse.Namespace, config: dict[str, Any], cwd: Path) -> Settings:
    default_project = slugify(cwd.name)
    output_dir = Path(cfg_value(args, config, "output_dir", "lit-watch/runs")).expanduser()
    wiki_dir = Path(cfg_value(args, config, "wiki_dir", "research-wiki")).expanduser()
    openalex_skill_dir = Path(
        cfg_value(args, config, "openalex_skill_dir", "crates/runtime/assets/skills/openalex-search")
    ).expanduser()
    reviewer_direction_file_raw = cfg_value(args, config, "reviewer_direction_file", None)
    reviewer_direction_file = (
        Path(reviewer_direction_file_raw).expanduser() if reviewer_direction_file_raw else None
    )

    return Settings(
        project=str(cfg_value(args, config, "project", default_project)),
        topic=cfg_value(args, config, "topic", None),
        output_dir=output_dir,
        wiki_dir=wiki_dir,
        openalex_skill_dir=openalex_skill_dir,
        aris_bin=cfg_value(args, config, "aris_bin", None),
        model=cfg_value(args, config, "model", None),
        permission_mode=str(cfg_value(args, config, "permission_mode", DEFAULT_PERMISSION_MODE)),
        lookback_days=int(cfg_value(args, config, "lookback_days", DEFAULT_LOOKBACK_DAYS)),
        max_results_per_query=int(
            cfg_value(args, config, "max_results_per_query", DEFAULT_MAX_RESULTS_PER_QUERY)
        ),
        dry_run_only=bool(args.dry_run_only or config.get("dry_run_only", False)),
        allowed_tools=cfg_value(args, config, "allowed_tools", None),
        reviewer_direction_file=reviewer_direction_file,
        extra_instruction=cfg_value(args, config, "extra_instruction", None),
    )


def slugify(value: str, max_length: int = 80) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9._-]+", "-", value)
    value = re.sub(r"-{2,}", "-", value).strip("-")
    if len(value) > max_length:
        value = value[:max_length].rstrip("-._")
    return value or "project"


def read_text(path: Path, limit: int, tail: bool = False) -> str:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return ""
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    return text[-limit:] if tail and len(text) > limit else text[:limit]


def build_wiki_context(wiki_dir: Path) -> str:
    parts: list[str] = []
    for label, relative, limit, tail in [
        ("query_pack", "query_pack.md", 12_000, False),
        ("gap_map", "gap_map.md", 8_000, False),
        ("index", "index.md", 6_000, False),
        ("recent_log", "log.md", 6_000, True),
    ]:
        content = read_text(wiki_dir / relative, limit=limit, tail=tail)
        if content.strip():
            parts.append(f"## {label}\n\n{content.strip()}")
    if not parts:
        return "No research-wiki context was found. Infer from the provided topic if present."
    return "\n\n".join(parts)


def resolve_aris_command(settings: Settings, cwd: Path) -> list[str]:
    if settings.aris_bin:
        return [str(Path(settings.aris_bin).expanduser())]
    local_bin = cwd / "target" / "debug" / "aris"
    if local_bin.exists():
        return [str(local_bin)]
    cargo = shutil.which("cargo")
    if cargo:
        return [cargo, "run", "-p", "aris-cli", "--"]
    raise SystemExit("Could not find target/debug/aris or cargo. Build ARIS first.")


def build_prompt(
    settings: Settings,
    cwd: Path,
    run_dir: Path,
    reviewer_direction_text: str | None = None,
) -> str:
    now = dt.datetime.now(dt.timezone.utc)
    to_date = now.date()
    from_date = to_date - dt.timedelta(days=settings.lookback_days)
    query_plan = run_dir / "openalex_queries.json"
    openalex_out = run_dir / "openalex"
    reviewer_path = run_dir / "reviewer_direction.md"
    summary_path = run_dir / "SUMMARY.md"
    skill_dir = settings.openalex_skill_dir
    if not skill_dir.is_absolute():
        skill_dir = cwd / skill_dir
    script_path = skill_dir.resolve() / "scripts" / "openalex_works_export.py"
    wiki_dir = settings.wiki_dir if settings.wiki_dir.is_absolute() else cwd / settings.wiki_dir
    wiki_context = build_wiki_context(wiki_dir)
    max_results_line = (
        "Run the complete export without --max-results."
        if settings.max_results_per_query == 0
        else f"Use --max-results {settings.max_results_per_query} per query for this scheduled pass."
    )
    full_export_line = (
        "Stop after dry-run counts and write a dry-run-only SUMMARY.md."
        if settings.dry_run_only
        else "After dry-run review and query tightening, run the full export."
    )
    topic_line = settings.topic or "Infer the next best direction from research-wiki."
    extra = f"\n\nExtra instruction:\n{settings.extra_instruction.strip()}" if settings.extra_instruction else ""
    if reviewer_direction_text:
        reviewer_goal = textwrap.dedent(
            """
            1. Use the Codex reviewer decision that has already been saved for this run.
            2. As executor, invoke the skill named "openalex-search" and run that search.
            3. Export metadata, summarize findings, and update research-wiki.
            """
        ).strip()
        reviewer_protocol = textwrap.dedent(
            f"""
            - Do not call LlmReview in this run. Codex already performed the reviewer step.
            - Read and preserve the reviewer decision saved at {reviewer_path}.
            - Treat the Codex reviewer decision below as the authority for this pass.
            - Then call the Skill tool with skill="openalex-search".
            """
        ).strip()
        reviewer_section = f"\n\nCodex reviewer decision:\n{reviewer_direction_text.strip()}\n"
    else:
        reviewer_goal = textwrap.dedent(
            """
            1. Ask the ARIS reviewer model to critique the current research-wiki state.
            2. Let the reviewer identify which missing research direction should be searched next.
            3. As executor, invoke the skill named "openalex-search" and run that search.
            4. Export metadata, summarize findings, and update research-wiki.
            """
        ).strip()
        reviewer_protocol = textwrap.dedent(
            f"""
            - First call LlmReview. Ask the reviewer to inspect the research-wiki context below and decide what research direction is still missing.
            - The reviewer prompt must ask for: priority direction, why it matters, what to avoid repeating, 2 to 5 OpenAlex query families, expected relevant venues/topics, and stop criteria.
            - Save the reviewer's answer to {reviewer_path}.
            - Then call the Skill tool with skill="openalex-search".
            """
        ).strip()
        reviewer_section = ""

    header = f"""
You are running a scheduled ARIS literature-watch pass.

Goal:
{reviewer_goal}

Project: {settings.project}
Topic anchor: {topic_line}
Working directory: {cwd}
Run directory: {run_dir}
Reviewer decision path: {reviewer_path}
OpenAlex query-plan path: {query_plan}
OpenAlex export directory: {openalex_out}
OpenAlex export script: {script_path}
Summary path: {summary_path}
Freshness window: {from_date.isoformat()} to {to_date.isoformat()}

Required execution protocol:
{reviewer_protocol}
- As the executor model, create {query_plan} as JSON with 2 to 5 named query expressions derived from the reviewer's recommendation.
- Use a shared OpenAlex filter similar to:
  from_publication_date:{from_date.isoformat()},to_publication_date:{to_date.isoformat()},type:article,language:en,is_retracted:false,is_paratext:false
- Include both broad `search` expressions and at least one precise `title_and_abstract.search` expression when appropriate.
- Run the OpenAlex script with --dry-run and inspect query_counts.csv.
- Quote every filesystem path in shell commands because this workspace path contains spaces.
- Tighten queries that are empty, too broad, or off-topic.
- {full_export_line}
- {max_results_line}
- Write {summary_path} with: reviewer recommendation, executor interpretation, exact search formula, dry-run counts, export paths, top papers, gaps, and what to search next.
- If {wiki_dir} exists, update it with the most relevant new papers and append a log entry.
- If blocked, write {run_dir / "BLOCKED.md"} with the exact reason and the next manual command.

Research-wiki context:
""".strip()
    return f"{header}\n{wiki_context}{reviewer_section}{extra}\n"


def main() -> int:
    args = parse_args()
    cwd = Path.cwd().resolve()
    config = load_config(args.config)
    settings = make_settings(args, config, cwd)

    timestamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    topic_slug = slugify(settings.topic or "auto")
    run_dir = (settings.output_dir / f"{timestamp}-{topic_slug}").resolve()
    run_dir.mkdir(parents=True, exist_ok=True)

    reviewer_direction_text = None
    reviewer_source = "aris-llm-review"
    if settings.reviewer_direction_file:
        reviewer_source_path = (
            settings.reviewer_direction_file
            if settings.reviewer_direction_file.is_absolute()
            else cwd / settings.reviewer_direction_file
        )
        reviewer_direction_text = read_text(reviewer_source_path, limit=20_000)
        if not reviewer_direction_text.strip():
            raise SystemExit(f"Reviewer direction file is missing or empty: {reviewer_source_path}")
        (run_dir / "reviewer_direction.md").write_text(
            reviewer_direction_text.strip() + "\n",
            encoding="utf-8",
        )
        reviewer_source = f"codex-file:{reviewer_source_path}"

    prompt = build_prompt(settings, cwd, run_dir, reviewer_direction_text=reviewer_direction_text)
    prompt_path = run_dir / "prompt.md"
    prompt_path.write_text(prompt, encoding="utf-8")

    if args.print_prompt:
        print(prompt)
        print(f"\nPrompt written to {prompt_path}")
        return 0

    command = resolve_aris_command(settings, cwd)
    if settings.model:
        command.extend(["--model", settings.model])
    if settings.permission_mode:
        command.extend(["--permission-mode", settings.permission_mode])
    if settings.allowed_tools:
        command.extend(["--allowedTools", settings.allowed_tools])
    command.extend(["prompt", prompt])

    manifest = {
        "started_at": dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat(),
        "cwd": str(cwd),
        "run_dir": str(run_dir),
        "command": command[:-1] + ["<prompt>"],
        "settings": {
            "project": settings.project,
            "topic": settings.topic,
            "wiki_dir": str(settings.wiki_dir),
            "openalex_skill_dir": str(settings.openalex_skill_dir),
            "lookback_days": settings.lookback_days,
            "max_results_per_query": settings.max_results_per_query,
            "dry_run_only": settings.dry_run_only,
            "reviewer_source": reviewer_source,
            "reviewer_direction_file": str(settings.reviewer_direction_file)
            if settings.reviewer_direction_file
            else None,
        },
    }
    (run_dir / "watch_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    (run_dir / "aris.stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (run_dir / "aris.stderr.txt").write_text(completed.stderr, encoding="utf-8")

    if completed.returncode != 0:
        blocked_path = run_dir / "BLOCKED.md"
        stderr_tail = completed.stderr[-4_000:] if completed.stderr else "(empty stderr)"
        stdout_tail = completed.stdout[-2_000:] if completed.stdout else "(empty stdout)"
        blocked_path.write_text(
            textwrap.dedent(
                f"""
                # ARIS Literature Watch Blocked

                ARIS exited with code {completed.returncode}.

                ## Next Manual Check

                Inspect:

                - {run_dir / "aris.stderr.txt"}
                - {run_dir / "aris.stdout.txt"}

                If the error is a DNS, model API, or OpenAlex network failure, rerun after enabling network access for this command.

                ## stderr tail

                ```text
                {stderr_tail}
                ```

                ## stdout tail

                ```text
                {stdout_tail}
                ```
                """
            ).strip()
            + "\n",
            encoding="utf-8",
        )
        print(f"ARIS literature-watch pass failed with exit code {completed.returncode}.")
        print(f"Run directory: {run_dir}")
        print(f"stderr: {run_dir / 'aris.stderr.txt'}")
        print(f"blocked: {blocked_path}")
        return completed.returncode

    print("ARIS literature-watch pass completed.")
    print(f"Run directory: {run_dir}")
    print(f"Summary: {run_dir / 'SUMMARY.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
