#!/usr/bin/env python3
"""Build a focused AAAI 2026 LLM Agents & Tool Use paper collection."""

from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from pypdf import PdfReader


PRIMARY_CLASSES = [
    "Agent Benchmarks & Evaluation",
    "Multi-Agent Collaboration & Orchestration",
    "Tool Use, Tool Creation & Workflow Automation",
    "RAG, Memory & Knowledge Grounding",
    "Reasoning, Planning & Decision Making",
    "Agent Training, Optimization & Adaptation",
    "Safety, Alignment, Auditing & Security",
    "Domain Agent Applications",
]

PRIMARY_OVERRIDES_BY_ARTICLE_ID = {
    "42382": "Agent Benchmarks & Evaluation",
    "42373": "Tool Use, Tool Creation & Workflow Automation",
    "42377": "RAG, Memory & Knowledge Grounding",
    "42384": "Domain Agent Applications",
    "42361": "RAG, Memory & Knowledge Grounding",
    "42170": "RAG, Memory & Knowledge Grounding",
    "42222": "Multi-Agent Collaboration & Orchestration",
    "42283": "Domain Agent Applications",
    "41064": "Agent Training, Optimization & Adaptation",
    "41058": "Safety, Alignment, Auditing & Security",
    "41054": "Safety, Alignment, Auditing & Security",
    "41065": "Safety, Alignment, Auditing & Security",
    "41134": "Safety, Alignment, Auditing & Security",
    "41231": "Domain Agent Applications",
    "41311": "Domain Agent Applications",
    "37014": "Agent Benchmarks & Evaluation",
    "37020": "RAG, Memory & Knowledge Grounding",
    "37052": "Multi-Agent Collaboration & Orchestration",
    "37113": "Agent Benchmarks & Evaluation",
    "37154": "Domain Agent Applications",
    "37169": "Domain Agent Applications",
    "37209": "Agent Benchmarks & Evaluation",
    "37164": "Domain Agent Applications",
    "37152": "Agent Training, Optimization & Adaptation",
    "42470": "Domain Agent Applications",
    "42439": "Safety, Alignment, Auditing & Security",
    "38095": "Safety, Alignment, Auditing & Security",
    "42123": "Domain Agent Applications",
    "42120": "Multi-Agent Collaboration & Orchestration",
    "42127": "Domain Agent Applications",
    "38832": "Multi-Agent Collaboration & Orchestration",
    "38867": "Domain Agent Applications",
    "41447": "Domain Agent Applications",
    "41441": "Domain Agent Applications",
    "41425": "RAG, Memory & Knowledge Grounding",
    "41465": "Agent Training, Optimization & Adaptation",
    "41491": "Domain Agent Applications",
    "41464": "Domain Agent Applications",
    "41495": "Tool Use, Tool Creation & Workflow Automation",
    "39026": "RAG, Memory & Knowledge Grounding",
    "39205": "RAG, Memory & Knowledge Grounding",
    "39374": "Agent Benchmarks & Evaluation",
    "39395": "Tool Use, Tool Creation & Workflow Automation",
    "39598": "Agent Benchmarks & Evaluation",
    "39773": "RAG, Memory & Knowledge Grounding",
    "39739": "Agent Training, Optimization & Adaptation",
    "39742": "Multi-Agent Collaboration & Orchestration",
    "39812": "Tool Use, Tool Creation & Workflow Automation",
    "39818": "Agent Benchmarks & Evaluation",
    "40026": "Multi-Agent Collaboration & Orchestration",
    "40204": "Multi-Agent Collaboration & Orchestration",
    "40221": "Domain Agent Applications",
    "40224": "Safety, Alignment, Auditing & Security",
    "40212": "Multi-Agent Collaboration & Orchestration",
    "40195": "Multi-Agent Collaboration & Orchestration",
    "40215": "Domain Agent Applications",
    "40222": "Agent Training, Optimization & Adaptation",
    "40228": "Agent Training, Optimization & Adaptation",
    "40223": "Tool Use, Tool Creation & Workflow Automation",
    "40237": "Domain Agent Applications",
    "40236": "Multi-Agent Collaboration & Orchestration",
    "40177": "Domain Agent Applications",
    "40189": "Tool Use, Tool Creation & Workflow Automation",
    "40210": "Safety, Alignment, Auditing & Security",
    "40181": "Multi-Agent Collaboration & Orchestration",
    "40279": "Agent Training, Optimization & Adaptation",
    "40313": "RAG, Memory & Knowledge Grounding",
    "40285": "Multi-Agent Collaboration & Orchestration",
    "40288": "Multi-Agent Collaboration & Orchestration",
    "40389": "Tool Use, Tool Creation & Workflow Automation",
    "40529": "RAG, Memory & Knowledge Grounding",
    "40453": "Agent Training, Optimization & Adaptation",
    "40487": "Multi-Agent Collaboration & Orchestration",
    "40640": "Agent Benchmarks & Evaluation",
    "40676": "Tool Use, Tool Creation & Workflow Automation",
    "40763": "Tool Use, Tool Creation & Workflow Automation",
    "40824": "Safety, Alignment, Auditing & Security",
    "40794": "Agent Training, Optimization & Adaptation",
    "41346": "Safety, Alignment, Auditing & Security",
    "40874": "Safety, Alignment, Auditing & Security",
}

THEME_RULES = [
    ("Benchmarking & Evaluation", r"benchmark|evaluation|evaluating|assess|assessment|metric|dataset|leaderboard|testbed"),
    ("Multi-Agent Collaboration", r"multi-agent|multiagent|multi agent|collaborative|collaboration|team|coopetition|society|multi-disciplinary|role-based"),
    ("Tool Use & Tool Creation", r"\btool\b|tools|tool-augmented|tool creation|api|agent-ready|workflow|data interaction|operation|copilot"),
    ("RAG & Evidence Grounding", r"\bRAG\b|retrieval|evidence|citation|grounded|grounding|knowledge-grounded|knowledge guided|knowledge-guided"),
    ("Memory & Knowledge Utilization", r"memory|knowledge|ontology|case based|case-based|knowledge base|self-evolving"),
    ("Reasoning & Planning", r"reasoning|planning|planner|logic|chain-of-thought|decision|mcts|tree search|bandit|optimization|policy"),
    ("Safety, Alignment & Ethics", r"alignment|aligned|moral|ethical|ethic|risk|audit|auditing|privacy|safe|safety|jailbreak|attack|defense|anomaly"),
    ("Simulation & Environment Agents", r"simulation|simulat|environment|population|disaster|social media|agent-based"),
    ("Learning & Adaptation", r"reinforcement learning|preference optimization|adaptive|self-evolving|fine-tuning|training|learn"),
]

DOMAIN_RULES = [
    ("Healthcare & Medicine", r"medical|medicine|clinical|health|disease|drug|surgical|treatment|diagnosis|rare disease"),
    ("Finance & Economics", r"finance|financial|equity|market|alpha|economic|redistricting"),
    ("Education", r"education|student|pedagogical|tutoring|reflection assessment|teaching"),
    ("Software Engineering & Code", r"software development|codebase|code generation|programming|programmatic|reverse engineering|design verification|ODRL|repository"),
    ("Recommender Systems", r"recommend|recommender|recommendation"),
    ("Science & Engineering", r"science|engineering|manufacturing|energy|protein|drug discovery|chemistry"),
    ("Governance, Ethics & Policy", r"moral|ethical|policy|political|redistricting|professional role|fair"),
    ("Cybersecurity", r"security|jailbreak|attack|defense|risk auditing|risks auditing|privacy|tampering|offensive security"),
    ("Social Simulation & Disaster Response", r"social media|population|disaster|simulation|natural disasters"),
    ("Multimodal & Video", r"video|visual|vision|multimodal|mllm|image|scene|xr"),
    ("Enterprise & Operations", r"enterprise|operations|asset|due diligence|workflow|business|industrial|financial operations|career recommendation"),
]

PRIMARY_RULES = [
    ("Safety, Alignment, Auditing & Security", r"alignment|aligned|moral|ethical|ethic|risk|audit|auditing|privacy|safe|safety|jailbreak|attack|defense|anomaly|resilience"),
    ("Agent Benchmarks & Evaluation", r"benchmark|evaluation|evaluating|assess|assessment|metric|dataset|leaderboard|testbed"),
    ("RAG, Memory & Knowledge Grounding", r"\bRAG\b|retrieval|evidence|citation|grounded|grounding|memory|knowledge|ontology|case based|case-based|knowledge base"),
    ("Tool Use, Tool Creation & Workflow Automation", r"\btool\b|tools|tool-augmented|tool creation|api|agent-ready|workflow|data interaction|copilot|assistant"),
    ("Reasoning, Planning & Decision Making", r"reasoning|planning|planner|logic|chain-of-thought|decision|mcts|tree search|bandit|optimization|policy"),
    ("Multi-Agent Collaboration & Orchestration", r"multi-agent|multiagent|multi agent|collaborative|collaboration|team|coopetition|society|role-based|orchestrat"),
]

FIELDNAMES = [
    "collection_id",
    "primary_class",
    "themes",
    "domains",
    "paper_type",
    "primary_category",
    "official_section",
    "issue_number",
    "article_id",
    "title",
    "authors",
    "pages",
    "abstract",
    "method_cue",
    "page_url",
    "pdf_url",
    "source_local_path",
    "collection_pdf_path",
    "text_path",
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="awesome-aaai-2026-papers/llm_related_core_papers.jsonl")
    parser.add_argument("--out-dir", default="awesome-aaai-2026-papers/llm-agents-tool-use")
    parser.add_argument("--copy-pdfs", action="store_true", default=True)
    return parser


def slugify(value: str, max_len: int = 120) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^A-Za-z0-9]+", "-", value).strip("-").lower()
    return (value[:max_len].strip("-") or "untitled")


def compact_spaces(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def extract_pdf_text(path: Path) -> tuple[str, int]:
    reader = PdfReader(str(path))
    chunks: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        try:
            text = page.extract_text() or ""
        except Exception as exc:  # noqa: BLE001 - preserve failure context in text
            text = f"\n[Text extraction failed on page {page_number}: {type(exc).__name__}: {exc}]\n"
        chunks.append(f"\n\n--- Page {page_number} ---\n{text}")
    return "\n".join(chunks).strip(), len(reader.pages)


def extract_section(text: str, start_patterns: list[str], stop_patterns: list[str], max_chars: int) -> str:
    normalized = text.replace("\r", "\n")
    start_match = None
    for pattern in start_patterns:
        match = re.search(pattern, normalized, re.IGNORECASE | re.MULTILINE)
        if match and (start_match is None or match.start() < start_match.start()):
            start_match = match
    if not start_match:
        return ""

    start = start_match.end()
    stop = min(len(normalized), start + max_chars)
    for pattern in stop_patterns:
        match = re.search(pattern, normalized[start:stop], re.IGNORECASE | re.MULTILINE)
        if match:
            stop = start + match.start()
            break
    return compact_spaces(normalized[start:stop])[:max_chars].strip()


def extract_abstract(text: str) -> str:
    abstract = extract_section(
        text,
        [r"\bAbstract\b[:\s]*"],
        [
            r"\n\s*(?:1\s*)?Introduction\b",
            r"\n\s*Keywords\b",
            r"\n\s*CCS Concepts\b",
            r"\n\s*1\s+[A-Z][A-Za-z ]{3,}\n",
        ],
        2600,
    )
    if abstract:
        return abstract
    first_page = text.split("--- Page 2 ---", 1)[0]
    return compact_spaces(first_page)[:1600]


def extract_method_cue(text: str) -> str:
    method = extract_section(
        text,
        [
            r"\n\s*(?:2|3)?\.?\s*(?:Method|Methodology|Approach|Framework|The Proposed|Our Approach|System|Model)\b[:\s]*",
            r"\n\s*(?:Method|Methodology|Approach|Framework|System Overview)\b[:\s]*",
        ],
        [
            r"\n\s*(?:Experiment|Experiments|Evaluation|Results|Related Work|Conclusion)\b",
            r"\n\s*\d+\.?\s+[A-Z][A-Za-z ]{3,}\n",
        ],
        1800,
    )
    if method:
        return method
    intro = extract_section(
        text,
        [r"\n\s*(?:1\s*)?Introduction\b[:\s]*"],
        [r"\n\s*(?:2\s*)?(?:Related Work|Background|Method|Preliminaries)\b"],
        1800,
    )
    return intro


def match_labels(haystack: str, rules: list[tuple[str, str]]) -> list[str]:
    labels = [name for name, pattern in rules if re.search(pattern, haystack, re.IGNORECASE)]
    return labels


def infer_primary(record: dict[str, Any], haystack: str) -> str:
    article_id = str(record.get("article_id", ""))
    if article_id in PRIMARY_OVERRIDES_BY_ARTICLE_ID:
        return PRIMARY_OVERRIDES_BY_ARTICLE_ID[article_id]
    for label, pattern in PRIMARY_RULES:
        if re.search(pattern, haystack, re.IGNORECASE):
            return label
    return "Domain Agent Applications"


def infer_paper_type(record: dict[str, Any], haystack: str) -> str:
    section = record.get("official_section", "")
    title = record.get("title", "")
    if "Demonstration" in section:
        return "Demo / System"
    if "Student Abstract" in section:
        return "Student Abstract"
    if "Doctoral Consortium" in section:
        return "Doctoral Consortium"
    if re.search(r"benchmark|dataset|evaluation", haystack, re.IGNORECASE):
        return "Benchmark / Evaluation"
    if re.search(r"framework|system|agent|architecture|tool", title, re.IGNORECASE):
        return "Method / System"
    return "Research Paper"


def markdown_escape(text: str) -> str:
    return (text or "").replace("[", "\\[").replace("]", "\\]")


def markdown_target(path_or_url: str) -> str:
    return (path_or_url or "").replace(" ", "%20").replace("(", "%28").replace(")", "%29")


def short_authors(authors: str, limit: int = 3) -> str:
    parts = [part.strip() for part in (authors or "").split(",") if part.strip()]
    if not parts:
        return "Authors not listed"
    if len(parts) <= limit:
        return ", ".join(parts)
    return ", ".join(parts[:limit]) + " et al"


def paper_line(row: dict[str, Any]) -> str:
    themes = ", ".join(row["themes"][:4])
    domains = ", ".join(row["domains"][:3]) if row["domains"] else "General"
    local_pdf_target = f"pdfs/{Path(row['collection_pdf_path']).name}"
    return (
        f"- [{markdown_escape(row['title'])}]({markdown_target(row['page_url'])}) - "
        f"{markdown_escape(short_authors(row['authors']))}. "
        f"{markdown_escape(row['official_section'])}, pp. {row.get('pages', '')}. "
        f"[PDF]({markdown_target(row['pdf_url'])}) | "
        f"[Local PDF]({markdown_target(local_pdf_target)}). "
        f"Themes: {markdown_escape(themes)}. Domains: {markdown_escape(domains)}."
    )


def build_readme(rows: list[dict[str, Any]]) -> str:
    primary_counts = Counter(row["primary_class"] for row in rows)
    theme_counts = Counter(theme for row in rows for theme in row["themes"])
    domain_counts = Counter(domain for row in rows for domain in row["domains"])
    type_counts = Counter(row["paper_type"] for row in rows)
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["primary_class"]].append(row)

    lines = [
        "# AAAI 2026 LLM Agents & Tool Use Papers",
        "",
        "A focused local collection of the 80 AAAI 2026 core LLM papers tagged as **LLM Agents & Tool Use**.",
        "",
        f"- Papers: **{len(rows)}**",
        "- Selection source: `awesome-aaai-2026-papers/llm_related_core_papers.jsonl`",
        "- Reading basis: extracted PDF text, with title, abstract, introduction/method cues, official OJS track, and metadata.",
        "- Folder view: `by-primary-class/` contains class-specific PDF links.",
        "",
        "## Classification Overview",
        "",
        "### Primary Classes",
        "",
    ]
    for label, count in primary_counts.most_common():
        lines.append(f"- {label}: {count}")

    lines.extend(["", "### Cross-Cutting Themes", ""])
    for label, count in theme_counts.most_common():
        lines.append(f"- {label}: {count}")

    lines.extend(["", "### Application Domains", ""])
    for label, count in domain_counts.most_common():
        lines.append(f"- {label}: {count}")

    lines.extend(["", "### Paper Types", ""])
    for label, count in type_counts.most_common():
        lines.append(f"- {label}: {count}")

    lines.extend(["", "## Papers by Primary Class", ""])
    order = [label for label in PRIMARY_CLASSES if label in grouped] + sorted(
        set(grouped) - set(PRIMARY_CLASSES)
    )
    for label in order:
        label_rows = sorted(
            grouped[label],
            key=lambda row: (row["primary_category"], row["issue_number"], row["title"]),
        )
        lines.extend(["", f"### {label} ({len(label_rows)})", ""])
        for row in label_rows:
            lines.append(paper_line(row))

    lines.append("")
    return "\n".join(lines)


def safe_symlink(target: Path, link_path: Path) -> None:
    link_path.parent.mkdir(parents=True, exist_ok=True)
    if link_path.is_symlink():
        current = os.readlink(link_path)
        if current == os.path.relpath(target, start=link_path.parent):
            return
        link_path.unlink()
    if link_path.exists():
        return
    relative_target = os.path.relpath(target, start=link_path.parent)
    link_path.symlink_to(relative_target)


def build_category_folders(out_dir: Path, rows: list[dict[str, Any]]) -> None:
    base = out_dir / "by-primary-class"
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        grouped[row["primary_class"]].append(row)

    for label in PRIMARY_CLASSES:
        if label not in grouped:
            continue
        category_dir = base / slugify(label, 80)
        category_dir.mkdir(parents=True, exist_ok=True)
        category_lines = [f"# {label}", "", f"Papers: **{len(grouped[label])}**", ""]
        for row in sorted(grouped[label], key=lambda item: item["collection_id"]):
            pdf_path = Path(row["collection_pdf_path"])
            note_path = Path(row["note_path"])
            pdf_link = category_dir / pdf_path.name
            note_link = category_dir / note_path.name
            safe_symlink(pdf_path, pdf_link)
            safe_symlink(note_path, note_link)
            category_lines.append(
                f"- [{markdown_escape(row['title'])}]({markdown_target(pdf_path.name)}) "
                f"([note]({markdown_target(note_path.name)}))"
            )
        (category_dir / "README.md").write_text("\n".join(category_lines) + "\n", encoding="utf-8")


def build_notes(row: dict[str, Any]) -> str:
    return "\n".join(
        [
            f"# {row['title']}",
            "",
            f"- Collection ID: `{row['collection_id']}`",
            f"- Primary class: {row['primary_class']}",
            f"- Themes: {', '.join(row['themes'])}",
            f"- Domains: {', '.join(row['domains']) if row['domains'] else 'General'}",
            f"- Official section: {row['official_section']}",
            f"- Paper type: {row['paper_type']}",
            f"- Page URL: {row['page_url']}",
            f"- PDF URL: {row['pdf_url']}",
            f"- Local PDF: {row['collection_pdf_path']}",
            "",
            "## Abstract",
            "",
            row.get("abstract", ""),
            "",
            "## Method / Introduction Cue",
            "",
            row.get("method_cue", ""),
            "",
        ]
    )


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDNAMES)
        writer.writeheader()
        for row in rows:
            output = {field: row.get(field, "") for field in FIELDNAMES}
            output["themes"] = "; ".join(row["themes"])
            output["domains"] = "; ".join(row["domains"])
            writer.writerow(output)


def main() -> int:
    args = build_parser().parse_args()
    out_dir = Path(args.out_dir)
    pdf_dir = out_dir / "pdfs"
    text_dir = out_dir / "texts"
    notes_dir = out_dir / "notes"
    for directory in [out_dir, pdf_dir, text_dir, notes_dir]:
        directory.mkdir(parents=True, exist_ok=True)

    source_rows = [
        row
        for row in read_jsonl(Path(args.input))
        if "LLM Agents & Tool Use" in row.get("llm_subthemes", [])
    ]
    source_rows.sort(key=lambda row: (row["primary_category"], row["issue_number"], row["title"]))

    collection_rows: list[dict[str, Any]] = []
    for index, row in enumerate(source_rows, start=1):
        article_id = row.get("article_id") or f"paper{index:03d}"
        stem = f"{index:03d}_{article_id}_{slugify(row['title'], 95)}"
        source_pdf = Path(row["local_path"])
        target_pdf = pdf_dir / f"{stem}.pdf"
        target_text = text_dir / f"{stem}.txt"
        target_note = notes_dir / f"{stem}.md"

        if args.copy_pdfs and (not target_pdf.exists() or target_pdf.stat().st_size != source_pdf.stat().st_size):
            shutil.copy2(source_pdf, target_pdf)

        text, page_count = extract_pdf_text(target_pdf)
        target_text.write_text(text, encoding="utf-8", errors="replace")
        abstract = extract_abstract(text)
        method_cue = extract_method_cue(text)
        reading_haystack = " ".join(
            [
                row.get("title", ""),
                row.get("official_section", ""),
                row.get("primary_category", ""),
                abstract,
            ]
        )
        domain_haystack = " ".join(
            [
                row.get("title", ""),
                row.get("official_section", ""),
                abstract[:900],
            ]
        )
        themes = match_labels(reading_haystack, THEME_RULES) or ["General Agentic LLM"]
        domains = match_labels(domain_haystack, DOMAIN_RULES)
        primary_class = infer_primary(row, reading_haystack)
        paper_type = infer_paper_type(row, reading_haystack)

        enriched = dict(row)
        enriched.update(
            {
                "collection_id": f"AGENT-{index:03d}",
                "source_local_path": row["local_path"],
                "collection_pdf_path": str(target_pdf),
                "text_path": str(target_text),
                "note_path": str(target_note),
                "page_count": page_count,
                "abstract": abstract,
                "method_cue": method_cue,
                "themes": themes,
                "domains": domains,
                "primary_class": primary_class,
                "paper_type": paper_type,
            }
        )
        target_note.write_text(build_notes(enriched), encoding="utf-8")
        collection_rows.append(enriched)

    write_jsonl(out_dir / "papers.jsonl", collection_rows)
    write_csv(out_dir / "papers.csv", collection_rows)
    summary = {
        "paper_count": len(collection_rows),
        "primary_class_counts": dict(Counter(row["primary_class"] for row in collection_rows).most_common()),
        "theme_counts": dict(Counter(theme for row in collection_rows for theme in row["themes"]).most_common()),
        "domain_counts": dict(Counter(domain for row in collection_rows for domain in row["domains"]).most_common()),
        "paper_type_counts": dict(Counter(row["paper_type"] for row in collection_rows).most_common()),
    }
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(build_readme(collection_rows), encoding="utf-8")
    build_category_folders(out_dir, collection_rows)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
