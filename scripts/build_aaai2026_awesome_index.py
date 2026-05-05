#!/usr/bin/env python3
"""Build an awesome-list style index for downloaded AAAI 2026 papers."""

from __future__ import annotations

import argparse
import csv
import json
import re
import time
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

try:
    import bs4
    import requests
    import urllib3
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(f"Missing dependency: {exc}") from exc


USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)
ROMAN_SUFFIX = re.compile(
    r"\s+(?:I|II|III|IV|V|VI|VII|VIII|IX|X|XI|XII|XIII|XIV|XV)$"
)


TECHNICAL_CATEGORY_ORDER = [
    "Application Domains",
    "Cognitive Modeling & Cognitive Systems",
    "Computer Vision",
    "Constraint Satisfaction and Optimization",
    "Data Mining & Knowledge Management",
    "Game Theory and Economic Paradigms",
    "Humans and AI",
    "Intelligent Robotics",
    "Knowledge Representation and Reasoning",
    "Machine Learning",
    "Multiagent Systems",
    "Natural Language Processing",
    "Philosophy and Ethics of AI",
    "Planning, Routing, and Scheduling",
    "Reasoning under Uncertainty",
    "Search and Optimization",
    "AI Alignment",
    "AI for Social Impact",
    "AAAI Journal Track",
    "AAAI Demonstration Track",
    "AAAI Emerging Trends in AI",
    "AAAI Student Abstract and Poster Program",
    "AAAI Doctoral Consortium Track",
    "AAAI Undergraduate Consortium",
    "Senior Member Presentation",
    "New Faculty Highlights",
    "IAAI: Emerging Applications of AI",
    "IAAI: Deployed Highly Innovative Applications of AI",
    "IAAI: Tools and Methodologies for Moving Faster and Safer",
    "EAAI: AI for Education",
    "EAAI: Main Track",
    "EAAI: Resources for Teaching AI in K-12",
    "EAAI: Model AI Assignments",
]


TAG_RULES = [
    ("LLMs & Foundation Models", r"\b(llm|llms|large language|foundation model|prompt|in-context|instruction|chatgpt|gpt)\b"),
    ("Agents & Tool Use", r"\b(agent|agents|agentic|tool-augmented|tool use|workflow|orchestrat|autonomous)\b"),
    ("Multi-Agent Systems", r"\b(multi-agent|multiagent|multi agent|agent collaboration|debate|council)\b"),
    ("RAG, Retrieval & QA", r"\b(rag|retrieval|retrieve|question answering|qa\b|knowledge base|document)\b"),
    ("Reasoning & Planning", r"\b(reasoning|planning|planner|tree search|monte carlo|mcts|chain-of-thought|cot|route|routing)\b"),
    ("Computer Vision", r"\b(image|vision|visual|object|segmentation|tracking|scene|camera|video|face|ocr)\b"),
    ("Video & Temporal Perception", r"\b(video|temporal|motion|action detection|trajectory|spatio-temporal|spatiotemporal)\b"),
    ("3D, Geometry & Embodiment", r"\b(3d|point cloud|gaussian splatting|splatting|nerf|mesh|pose|geometry|geometric)\b"),
    ("Multimodal Learning", r"\b(multimodal|multi-modal|cross-modal|vision-language|text-image|image-text|audio-visual|3d-text)\b"),
    ("Generative Models & Diffusion", r"\b(diffusion|generative|generation|generate|text-to|synthesis|gan|vae|flow matching)\b"),
    ("Graph Learning", r"\b(graph|gnn|hypergraph|node|edge|knowledge graph|subgraph)\b"),
    ("Reinforcement Learning", r"\b(reinforcement learning|rl\b|policy|reward|offline rl|online rl|bandit)\b"),
    ("Optimization & Search", r"\b(optimization|optimisation|search|constraint|scheduling|solver|integer programming|bayesian optimization)\b"),
    ("Robotics & Embodied AI", r"\b(robot|robotic|embodied|manipulation|grasp|navigation|locomotion|humanoid)\b"),
    ("Autonomous Driving & Transportation", r"\b(driving|autonomous vehicle|traffic|trajectory prediction|urban|vehicle|transportation)\b"),
    ("NLP", r"\b(nlp|language|text|translation|summarization|dialogue|dialog|sentence|semantic|token)\b"),
    ("Speech & Audio", r"\b(speech|audio|voice|speaker|acoustic|sound|paralinguistic)\b"),
    ("Recommendation & Ranking", r"\b(recommend|recommendation|ranking|ranker|preference)\b"),
    ("Time Series & Forecasting", r"\b(time series|forecast|forecasting|temporal|sensor|iot)\b"),
    ("Causal, Uncertainty & Probabilistic AI", r"\b(causal|causality|uncertainty|probabilistic|bayesian|conformal|counterfactual)\b"),
    ("Security, Privacy & Forensics", r"\b(security|privacy|private|attack|backdoor|jailbreak|adversarial|malware|vulnerabil|forensic|deepfake|poison)\b"),
    ("Trustworthy AI", r"\b(fairness|bias|robust|robustness|safe|safety|trust|explain|interpretable|interpretability|alignment)\b"),
    ("Healthcare, Bio & Molecules", r"\b(medical|health|clinical|disease|drug|protein|molecule|molecular|peptide|rna|dna|genomic|cancer|antibody)\b"),
    ("Science & Engineering AI", r"\b(scientific|physics|chemistry|crystal|materials?|pde|simulation|neural operator|energy)\b"),
    ("Education & Tutoring", r"\b(education|teaching|student|tutor|tutoring|assignment|learning analytics|k-12)\b"),
    ("Social Impact & Human-Centered AI", r"\b(social impact|human|society|mental health|misinformation|fake news|accessibility)\b"),
    ("Data Mining & Knowledge Management", r"\b(data mining|clustering|classification|anomaly|outlier|pattern mining|database)\b"),
    ("Evaluation, Benchmarks & Datasets", r"\b(benchmark|benchmarking|dataset|evaluation|metric|leaderboard|survey|empirical study)\b"),
    ("Code & Software Engineering", r"\b(code|programming|software|debug|vulnerability-fixing|commit|repository)\b"),
    ("Federated, Distributed & Efficient AI", r"\b(federated|distributed|efficient|compression|distillation|quantization|pruning|parameter-efficient|edge)\b"),
    ("Finance & Economics", r"\b(financial|finance|market|equity|economic|auction|game theory)\b"),
]


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default="data/aaai2026_metadata/manifest.jsonl")
    parser.add_argument("--issues", default="data/aaai2026_metadata/issues.json")
    parser.add_argument("--out-dir", default="awesome-aaai-2026-papers")
    parser.add_argument(
        "--sections-cache",
        default="data/aaai2026_metadata/official_sections.jsonl",
    )
    parser.add_argument("--refresh-sections", action="store_true")
    parser.add_argument("--timeout", type=int, default=90)
    parser.add_argument("--retries", type=int, default=6)
    parser.add_argument("--verify-tls", action="store_true")
    return parser


def compact_text(value: str) -> str:
    return re.sub(r"\s+", " ", value or "").strip()


def article_id_from_url(url: str) -> str:
    match = re.search(r"/article/view/(\d+)", url or "")
    return match.group(1) if match else ""


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def make_session(verify_tls: bool) -> requests.Session:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    session.verify = verify_tls
    return session


def fetch(session: requests.Session, url: str, timeout: int, retries: int) -> str:
    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except Exception as exc:  # noqa: BLE001 - retry and preserve context
            last_error = f"attempt {attempt}/{retries}: {type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(min(2**attempt, 15))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def scrape_official_sections(
    issues_path: Path,
    timeout: int,
    retries: int,
    verify_tls: bool,
) -> list[dict[str, Any]]:
    issues = json.loads(issues_path.read_text(encoding="utf-8"))
    session = make_session(verify_tls)
    rows: list[dict[str, Any]] = []

    for issue_index, issue in enumerate(issues, start=1):
        html = fetch(session, issue["issue_url"], timeout, retries)
        soup = bs4.BeautifulSoup(html, "html.parser")
        current_section = ""
        current_section_index = 0
        article_index = 0
        for node in soup.select("h2, .obj_article_summary"):
            if node.name == "h2":
                current_section = compact_text(node.get_text(" ", strip=True))
                current_section_index += 1
                continue
            if "obj_article_summary" not in (node.get("class") or []):
                continue

            article_index += 1
            title_link = node.select_one("h3.title a")
            pdf_link = node.select_one("a.obj_galley_link.pdf")
            page_url = title_link.get("href", "") if title_link else ""
            pdf_url = pdf_link.get("href", "") if pdf_link else ""
            rows.append(
                {
                    "issue_number": issue["issue_number"],
                    "issue_title": issue["issue_title"],
                    "issue_url": issue["issue_url"],
                    "article_index_in_issue": article_index,
                    "article_id": article_id_from_url(page_url or pdf_url),
                    "title": compact_text(title_link.get_text(" ", strip=True)) if title_link else "",
                    "official_section": current_section or "Uncategorized",
                    "section_index_in_issue": current_section_index,
                }
            )
        print(
            f"[{issue_index:02d}/{len(issues):02d}] "
            f"issue {issue['issue_number']:02d}: {article_index} sectioned papers",
            flush=True,
        )
    return rows


def normalize_category(section: str) -> str:
    section = compact_text(section)
    if section.startswith("AAAI Technical Track on "):
        section = section.removeprefix("AAAI Technical Track on ")
        return ROMAN_SUFFIX.sub("", section)

    replacements = {
        "AAAI Special Track on AI Alignment": "AI Alignment",
        "AAAI Special Track on AI for Social Impact I": "AI for Social Impact",
        "AAAI Special Track on AI for Social Impact II": "AI for Social Impact",
        "AAAI Journal Track": "AAAI Journal Track",
        "AAAI Demonstration Track": "AAAI Demonstration Track",
        "AAAI Emerging Trends in AI": "AAAI Emerging Trends in AI",
        "AAAI Student Abstract and Poster Program": "AAAI Student Abstract and Poster Program",
        "AAAI Doctoral Consortium Track": "AAAI Doctoral Consortium Track",
        "AAAI Undergraduate Consortium": "AAAI Undergraduate Consortium",
        "Senior Member Presentation": "Senior Member Presentation",
        "New Faculty Highlights": "New Faculty Highlights",
        "IAAI Technical Track on Emerging Applications of AI": "IAAI: Emerging Applications of AI",
        "IAAI Technical Track on Deployed Highly Innovative Applications of AI": "IAAI: Deployed Highly Innovative Applications of AI",
        "IAAI Technical Track on Tools and Methodologies for Moving Faster and Safer": "IAAI: Tools and Methodologies for Moving Faster and Safer",
        "EAAI Symposium: AI for Education": "EAAI: AI for Education",
        "EAAI Symposium: Main track": "EAAI: Main Track",
        "EAAI Symposium: Resources for Teaching AI in K-12": "EAAI: Resources for Teaching AI in K-12",
        "EAAI Symposium: Model AI Assignments": "EAAI: Model AI Assignments",
    }
    return replacements.get(section, ROMAN_SUFFIX.sub("", section))


def infer_topic_tags(record: dict[str, Any]) -> list[str]:
    haystack = " ".join(
        [
            record.get("title", ""),
            record.get("official_section", ""),
            record.get("primary_category", ""),
        ]
    ).lower()
    tags = [tag for tag, pattern in TAG_RULES if re.search(pattern, haystack)]
    if not tags:
        tags = [record.get("primary_category", "Uncategorized")]
    return tags[:8]


def markdown_escape(text: str) -> str:
    return text.replace("[", "\\[").replace("]", "\\]")


def markdown_link_target(path_or_url: str) -> str:
    return path_or_url.replace(" ", "%20").replace("(", "%28").replace(")", "%29")


def short_authors(authors: str, limit: int = 3) -> str:
    parts = [part.strip() for part in authors.split(",") if part.strip()]
    if not parts:
        return "Authors not listed"
    if len(parts) <= limit:
        return ", ".join(parts)
    return ", ".join(parts[:limit]) + " et al"


def category_anchor(category: str) -> str:
    anchor = category.lower()
    anchor = anchor.replace("&", "")
    anchor = re.sub(r"[^a-z0-9\s:-]", "", anchor)
    anchor = anchor.replace(":", "")
    anchor = re.sub(r"\s+", "-", anchor.strip())
    return anchor


def category_sort_key(category: str, count: int) -> tuple[int, int, str]:
    try:
        return (0, TECHNICAL_CATEGORY_ORDER.index(category), category)
    except ValueError:
        return (1, -count, category)


def enrich_records(
    manifest_rows: list[dict[str, Any]],
    section_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sections_by_id = {row["article_id"]: row for row in section_rows if row.get("article_id")}
    sections_by_issue_index = {
        (row["issue_number"], row["article_index_in_issue"]): row for row in section_rows
    }
    enriched: list[dict[str, Any]] = []

    for record in manifest_rows:
        article_id = record.get("article_id") or article_id_from_url(record.get("page_url", ""))
        section = sections_by_id.get(article_id) or sections_by_issue_index.get(
            (record["issue_number"], record["article_index_in_issue"]), {}
        )
        official_section = section.get("official_section", "Uncategorized")
        enriched_record = dict(record)
        enriched_record["article_id"] = article_id
        enriched_record["official_section"] = official_section
        enriched_record["primary_category"] = normalize_category(official_section)
        enriched_record["topic_tags"] = infer_topic_tags(enriched_record)
        enriched.append(enriched_record)
    return enriched


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fieldnames = [
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
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            output = {field: row.get(field, "") for field in fieldnames}
            output["topic_tags"] = "; ".join(row.get("topic_tags", []))
            writer.writerow(output)


def paper_line(record: dict[str, Any], out_dir: Path) -> str:
    title = markdown_escape(record["title"])
    authors = markdown_escape(short_authors(record.get("authors", "")))
    page_url = markdown_link_target(record.get("page_url", ""))
    pdf_url = markdown_link_target(record.get("pdf_url", ""))
    local_path = Path(record.get("local_path", ""))
    try:
        local_rel = markdown_link_target(str(Path("..") / local_path))
    except TypeError:
        local_rel = ""
    pages = f", pp. {record['pages']}" if record.get("pages") else ""
    tags = ", ".join(record.get("topic_tags", [])[:4])
    tag_text = f" Tags: {markdown_escape(tags)}." if tags else ""
    section = markdown_escape(record.get("official_section", ""))
    return (
        f"- [{title}]({page_url}) - {authors}. "
        f"{section}{pages}. [PDF]({pdf_url})"
        f"{' | [Local PDF](' + local_rel + ')' if local_rel else ''}."
        f"{tag_text}"
    )


def build_readme(out_dir: Path, rows: list[dict[str, Any]]) -> str:
    counts = Counter(row["primary_category"] for row in rows)
    categories = sorted(counts, key=lambda cat: category_sort_key(cat, counts[cat]))
    issue_count = len({row["issue_number"] for row in rows})
    tag_counts = Counter(tag for row in rows for tag in row.get("topic_tags", []))

    lines = [
        "# Awesome AAAI 2026 Papers",
        "",
        (
            "A local awesome-list style index for AAAI 2026 papers downloaded from "
            "the AAAI OJS Vol. 40 archive. Papers are grouped by the official OJS "
            "track heading, with cross-cutting topic tags inferred from titles and tracks."
        ),
        "",
        f"- Papers: **{len(rows)}**",
        f"- Issues: **{issue_count}**",
        f"- Primary categories: **{len(categories)}**",
        "- Source: [Proceedings of the AAAI Conference on Artificial Intelligence archive](https://ojs.aaai.org/index.php/AAAI/issue/archive)",
        "",
        "## Table of Contents",
        "",
    ]
    for category in categories:
        lines.append(f"- [{category} ({counts[category]})](#{category_anchor(category)})")

    lines.extend(
        [
            "",
            "## Cross-Cutting Topic Tags",
            "",
            "These tags are title/track-derived and can overlap; the primary grouping below remains the official OJS track family.",
            "",
        ]
    )
    for tag, count in tag_counts.most_common():
        lines.append(f"- {tag}: {count}")

    for category in categories:
        category_rows = sorted(
            [row for row in rows if row["primary_category"] == category],
            key=lambda row: (row["issue_number"], row["article_index_in_issue"]),
        )
        lines.extend(["", f'<a id="{category_anchor(category)}"></a>', f"## {category} ({len(category_rows)})", ""])
        for record in category_rows:
            lines.append(paper_line(record, out_dir))

    lines.append("")
    return "\n".join(lines)


def build_topic_tags_md(rows: list[dict[str, Any]]) -> str:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        for tag in row.get("topic_tags", []):
            grouped[tag].append(row)

    lines = [
        "# AAAI 2026 Papers by Cross-Cutting Topic Tag",
        "",
        "A paper can appear under multiple tags. Tags are inferred from titles plus official OJS track headings.",
        "",
    ]
    for tag, tag_rows in sorted(grouped.items(), key=lambda item: (-len(item[1]), item[0])):
        lines.extend(["", f"## {tag} ({len(tag_rows)})", ""])
        for record in sorted(tag_rows, key=lambda row: (row["primary_category"], row["issue_number"], row["article_index_in_issue"])):
            title = markdown_escape(record["title"])
            page_url = markdown_link_target(record.get("page_url", ""))
            category = markdown_escape(record["primary_category"])
            lines.append(f"- [{title}]({page_url}) - {category}. [PDF]({markdown_link_target(record.get('pdf_url', ''))})")
    lines.append("")
    return "\n".join(lines)


def build_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    category_counts = Counter(row["primary_category"] for row in rows)
    official_counts = Counter(row["official_section"] for row in rows)
    tag_counts = Counter(tag for row in rows for tag in row.get("topic_tags", []))
    return {
        "paper_count": len(rows),
        "issue_count": len({row["issue_number"] for row in rows}),
        "primary_category_count": len(category_counts),
        "official_section_count": len(official_counts),
        "primary_category_counts": dict(category_counts.most_common()),
        "official_section_counts": dict(official_counts.most_common()),
        "topic_tag_counts": dict(tag_counts.most_common()),
    }


def main() -> int:
    args = build_parser().parse_args()
    if not args.verify_tls:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    manifest_path = Path(args.manifest)
    issues_path = Path(args.issues)
    out_dir = Path(args.out_dir)
    sections_cache = Path(args.sections_cache)
    out_dir.mkdir(parents=True, exist_ok=True)

    manifest_rows = read_jsonl(manifest_path)
    if args.refresh_sections or not sections_cache.exists():
        print("Scraping official OJS section headings...", flush=True)
        section_rows = scrape_official_sections(
            issues_path,
            args.timeout,
            args.retries,
            args.verify_tls,
        )
        write_jsonl(sections_cache, section_rows)
    else:
        section_rows = read_jsonl(sections_cache)

    rows = enrich_records(manifest_rows, section_rows)
    rows.sort(key=lambda row: (row["primary_category"], row["issue_number"], row["article_index_in_issue"]))

    write_jsonl(out_dir / "papers.jsonl", rows)
    write_csv(out_dir / "papers.csv", rows)
    summary = build_summary(rows)
    (out_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "README.md").write_text(build_readme(out_dir, rows), encoding="utf-8")
    (out_dir / "TOPIC_TAGS.md").write_text(build_topic_tags_md(rows), encoding="utf-8")

    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
