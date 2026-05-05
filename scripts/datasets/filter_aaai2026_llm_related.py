#!/usr/bin/env python3
"""Create LLM-related subsets from the AAAI 2026 awesome index."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


CORE_LLM_PATTERN = re.compile(
    r"\b(?:LLM|LLMs|MLLM|MLLMs|LVLM|LVLMs)\b"
    r"|large language model"
    r"|large vision-language model"
    r"|large vision language model"
    r"|multimodal large language"
    r"|vision-language model"
    r"|vision language model"
    r"|foundation model"
    r"|ChatGPT"
    r"|\bGPT\b",
    re.IGNORECASE,
)

BROAD_LLM_ADJACENT_PATTERN = re.compile(
    r"prompt"
    r"|in-context"
    r"|instruction"
    r"|chain-of-thought"
    r"|\bRAG\b"
    r"|retrieval-augmented"
    r"|agent"
    r"|tool"
    r"|alignment"
    r"|jailbreak"
    r"|hallucination"
    r"|long-context"
    r"|pretraining"
    r"|fine-tuning"
    r"|\bLoRA\b",
    re.IGNORECASE,
)

SUBTHEME_RULES = [
    ("LLM Agents & Tool Use", r"agent|tool|workflow|orchestrat|multi-agent|multiagent"),
    ("RAG & Knowledge-Augmented LLMs", r"\bRAG\b|retrieval|knowledge|citation|evidence|ground"),
    ("Reasoning, Planning & CoT", r"reason|planning|planner|chain-of-thought|tree search|mcts|logic"),
    ("Alignment, Safety & Jailbreaks", r"alignment|safe|safety|jailbreak|attack|backdoor|red.team|risk|trust"),
    ("Evaluation, Benchmarks & Datasets", r"benchmark|evaluation|dataset|metric|leaderboard|assess"),
    ("Multimodal / Vision-Language LLMs", r"multimodal|multi-modal|vision-language|vision language|visual|image|video|audio|mllm|lvlm"),
    ("Efficient / Long-Context LLMs", r"efficient|compression|token|kv cache|long-context|long context|quantization|pruning|lora|adapter"),
    ("Domain LLM Applications", r"medical|health|drug|finance|financial|education|legal|science|engineering|software|code|robot|driving"),
    ("Foundation Models", r"foundation model"),
]

FIELDNAMES = [
    "llm_match_type",
    "llm_subthemes",
    "primary_category",
    "official_section",
    "topic_tags",
    "issue_number",
    "issue_title",
    "article_index_in_issue",
    "article_id",
    "title",
    "authors",
    "pages",
    "page_url",
    "pdf_url",
    "local_path",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="awesome-aaai-2026-papers/papers.jsonl")
    parser.add_argument("--out-dir", default="awesome-aaai-2026-papers")
    return parser


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            output = {field: row.get(field, "") for field in FIELDNAMES}
            output["topic_tags"] = "; ".join(row.get("topic_tags", []))
            output["llm_subthemes"] = "; ".join(row.get("llm_subthemes", []))
            writer.writerow(output)


def markdown_escape(text: str) -> str:
    return (text or "").replace("[", "\\[").replace("]", "\\]")


def markdown_target(text: str) -> str:
    return (text or "").replace(" ", "%20").replace("(", "%28").replace(")", "%29")


def short_authors(authors: str, limit: int = 3) -> str:
    parts = [part.strip() for part in (authors or "").split(",") if part.strip()]
    if not parts:
        return "Authors not listed"
    if len(parts) <= limit:
        return ", ".join(parts)
    return ", ".join(parts[:limit]) + " et al"


def classify_match(record: dict[str, Any]) -> str:
    title = record.get("title", "")
    if CORE_LLM_PATTERN.search(title):
        return "core"
    if "LLMs & Foundation Models" in record.get("topic_tags", []):
        return "tagged_adjacent"
    if BROAD_LLM_ADJACENT_PATTERN.search(title):
        return "broad_adjacent"
    return ""


def infer_subthemes(record: dict[str, Any]) -> list[str]:
    haystack = " ".join(
        [
            record.get("title", ""),
            record.get("primary_category", ""),
            record.get("official_section", ""),
            " ".join(record.get("topic_tags", [])),
        ]
    )
    themes = [name for name, pattern in SUBTHEME_RULES if re.search(pattern, haystack, re.IGNORECASE)]
    return themes or ["General LLM / Foundation Model"]


def enrich(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    broad: list[dict[str, Any]] = []
    for record in records:
        match_type = classify_match(record)
        if not match_type:
            continue
        item = dict(record)
        item["llm_match_type"] = match_type
        item["llm_subthemes"] = infer_subthemes(item)
        broad.append(item)

    broad.sort(key=lambda row: (row["primary_category"], row["issue_number"], row["article_index_in_issue"]))
    core = [row for row in broad if row["llm_match_type"] == "core"]
    return core, broad


def paper_line(record: dict[str, Any]) -> str:
    title = markdown_escape(record["title"])
    page_url = markdown_target(record.get("page_url", ""))
    pdf_url = markdown_target(record.get("pdf_url", ""))
    local_path = markdown_target("../" + record.get("local_path", ""))
    authors = markdown_escape(short_authors(record.get("authors", "")))
    section = markdown_escape(record.get("official_section", ""))
    pages = f", pp. {record['pages']}" if record.get("pages") else ""
    themes = markdown_escape(", ".join(record.get("llm_subthemes", [])[:4]))
    return (
        f"- [{title}]({page_url}) - {authors}. {section}{pages}. "
        f"[PDF]({pdf_url}) | [Local PDF]({local_path}). Themes: {themes}."
    )


def build_markdown(core: list[dict[str, Any]], broad: list[dict[str, Any]]) -> str:
    category_counts = Counter(row["primary_category"] for row in core)
    theme_counts = Counter(theme for row in core for theme in row.get("llm_subthemes", []))
    broad_counts = Counter(row["llm_match_type"] for row in broad)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in core:
        grouped[row["primary_category"]].append(row)

    lines = [
        "# AAAI 2026 LLM-Related Papers",
        "",
        "This is a focused subset of the local AAAI 2026 paper index.",
        "",
        "Selection policy:",
        "- **Core LLM-related**: title explicitly mentions LLM/LLMs, MLLM/LVLM, Large Language Model, Vision-Language Model, Foundation Model, GPT, or ChatGPT.",
        "- **Broad adjacent**: title or existing tags mention prompt, RAG, agent/tool use, alignment, jailbreak, hallucination, long-context, pretraining, fine-tuning, or similar LLM ecosystem terms.",
        "",
        f"- Core LLM-related papers: **{len(core)}**",
        f"- Broad LLM-adjacent candidates: **{len(broad)}**",
        f"- Core categories: **{len(category_counts)}**",
        "",
        "## Core Counts by Category",
        "",
    ]
    for category, count in category_counts.most_common():
        lines.append(f"- {category}: {count}")

    lines.extend(["", "## Core Counts by Subtheme", ""])
    for theme, count in theme_counts.most_common():
        lines.append(f"- {theme}: {count}")

    lines.extend(["", "## Broad Candidate Types", ""])
    for match_type, count in broad_counts.most_common():
        lines.append(f"- {match_type}: {count}")

    lines.extend(["", "## Core LLM-Related Papers", ""])
    for category, rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        lines.extend(["", f"### {category} ({len(rows)})", ""])
        for record in rows:
            lines.append(paper_line(record))

    lines.append("")
    return "\n".join(lines)


def build_summary(core: list[dict[str, Any]], broad: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "core_count": len(core),
        "broad_count": len(broad),
        "core_category_counts": dict(Counter(row["primary_category"] for row in core).most_common()),
        "core_subtheme_counts": dict(Counter(theme for row in core for theme in row.get("llm_subthemes", [])).most_common()),
        "broad_match_type_counts": dict(Counter(row["llm_match_type"] for row in broad).most_common()),
    }


def main() -> int:
    args = build_parser().parse_args()
    out_dir = Path(args.out_dir)
    rows = read_jsonl(Path(args.input))
    core, broad = enrich(rows)

    write_jsonl(out_dir / "llm_related_core_papers.jsonl", core)
    write_jsonl(out_dir / "llm_related_broad_papers.jsonl", broad)
    write_csv(out_dir / "llm_related_core_papers.csv", core)
    write_csv(out_dir / "llm_related_broad_papers.csv", broad)
    (out_dir / "LLM_RELATED.md").write_text(build_markdown(core, broad), encoding="utf-8")
    summary = build_summary(core, broad)
    (out_dir / "llm_related_summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
