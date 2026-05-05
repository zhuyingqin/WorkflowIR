#!/usr/bin/env python3
"""Download AAAI 2026 PDFs from the AAAI OJS archive.

The script first builds a manifest from the OJS archive pages, then downloads
every PDF linked from the Vol. 40 issue pages. It is intentionally resumable:
valid existing PDFs are skipped unless --force is passed.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import json
import os
import re
import sys
import threading
import time
import unicodedata
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

try:
    import bs4
    import requests
    import urllib3
except ImportError as exc:  # pragma: no cover - dependency guard
    raise SystemExit(f"Missing dependency: {exc}") from exc


ARCHIVE_URL = "https://ojs.aaai.org/index.php/AAAI/issue/archive"
USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/124.0.0.0 Safari/537.36"
)
PDF_MAGIC = b"%PDF"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scrape and download every AAAI 2026 PDF from AAAI OJS."
    )
    parser.add_argument("--archive-url", default=ARCHIVE_URL)
    parser.add_argument("--output-dir", default="data/aaai2026_papers")
    parser.add_argument("--metadata-dir", default="data/aaai2026_metadata")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--scrape-retries", type=int, default=6)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--archive-pages", type=int, default=4)
    parser.add_argument("--limit", type=int, default=0, help="Download only N PDFs.")
    parser.add_argument("--force", action="store_true", help="Redownload existing PDFs.")
    parser.add_argument("--list-only", action="store_true", help="Only write manifests.")
    parser.add_argument(
        "--verify-tls",
        action="store_true",
        help="Verify TLS certificates. Disabled by default because local Python certs may be stale.",
    )
    return parser


def make_session(verify_tls: bool) -> requests.Session:
    session = requests.Session()
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/pdf,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }
    )
    session.verify = verify_tls
    return session


def fetch_html(
    session: requests.Session,
    url: str,
    timeout: int,
    retries: int,
) -> bs4.BeautifulSoup:
    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            return bs4.BeautifulSoup(response.text, "html.parser")
        except Exception as exc:  # noqa: BLE001 - retry and report URL context
            last_error = f"attempt {attempt}/{retries}: {type(exc).__name__}: {exc}"
            if attempt < retries:
                time.sleep(min(2**attempt, 12))
    raise RuntimeError(f"failed to fetch {url}: {last_error}")


def issue_archive_url(archive_url: str, page_number: int) -> str:
    return archive_url if page_number == 1 else f"{archive_url.rstrip('/')}/{page_number}"


def text_clean(text: str) -> str:
    return re.sub(r"\s+", " ", text or "").strip()


def slugify(value: str, max_len: int = 120) -> str:
    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = value.strip("-")
    return (value[:max_len].strip("-") or "untitled")


def parse_issue_number(text: str) -> int | None:
    match = re.search(r"Vol\.\s*40\s+No\.\s*(\d+)", text)
    if not match:
        return None
    return int(match.group(1))


def collect_issues(
    session: requests.Session,
    archive_url: str,
    max_pages: int,
    timeout: int,
    retries: int,
) -> list[dict[str, Any]]:
    issues: list[dict[str, Any]] = []
    seen_urls: set[str] = set()
    saw_vol40 = False

    for page_number in range(1, max_pages + 1):
        url = issue_archive_url(archive_url, page_number)
        soup = fetch_html(session, url, timeout, retries)
        found_vol40_on_page = False

        for item in soup.select("li"):
            title_link = item.select_one("a.title")
            if not title_link or not title_link.get("href"):
                continue

            item_text = text_clean(item.get_text(" ", strip=True))
            issue_number = parse_issue_number(item_text)
            if issue_number is None:
                continue

            found_vol40_on_page = True
            saw_vol40 = True
            issue_url = title_link["href"]
            if issue_url in seen_urls:
                continue
            seen_urls.add(issue_url)
            title = text_clean(title_link.get_text(" ", strip=True))
            issues.append(
                {
                    "issue_number": issue_number,
                    "issue_title": title,
                    "issue_url": issue_url,
                    "archive_page": page_number,
                }
            )

        if saw_vol40 and page_number > 1 and not found_vol40_on_page:
            break

    issues.sort(key=lambda issue: issue["issue_number"])
    return issues


def article_id_from_url(url: str) -> str:
    match = re.search(r"/article/view/(\d+)", url)
    return match.group(1) if match else ""


def galley_id_from_pdf_url(url: str) -> str:
    match = re.search(r"/article/view/\d+/(\d+)", url)
    return match.group(1) if match else ""


def parse_issue(
    session: requests.Session,
    issue: dict[str, Any],
    timeout: int,
    retries: int,
) -> list[dict[str, Any]]:
    soup = fetch_html(session, issue["issue_url"], timeout, retries)
    records: list[dict[str, Any]] = []

    for article_index, article in enumerate(soup.select(".obj_article_summary"), start=1):
        title_link = article.select_one("h3.title a")
        pdf_link = article.select_one("a.obj_galley_link.pdf")
        if not title_link or not pdf_link or not pdf_link.get("href"):
            continue

        title = text_clean(title_link.get_text(" ", strip=True))
        page_url = title_link.get("href", "")
        pdf_url = pdf_link["href"]
        authors_node = article.select_one(".authors")
        pages_node = article.select_one(".pages")

        article_id = article_id_from_url(page_url or pdf_url)
        record = {
            "issue_number": issue["issue_number"],
            "issue_title": issue["issue_title"],
            "issue_url": issue["issue_url"],
            "article_index_in_issue": article_index,
            "article_id": article_id,
            "galley_id": galley_id_from_pdf_url(pdf_url),
            "title": title,
            "authors": text_clean(authors_node.get_text(" ", strip=True)) if authors_node else "",
            "pages": text_clean(pages_node.get_text(" ", strip=True)) if pages_node else "",
            "page_url": page_url,
            "pdf_url": pdf_url,
        }
        records.append(record)

    return records


def record_paths(record: dict[str, Any], output_dir: Path) -> tuple[Path, Path]:
    issue_number = int(record["issue_number"])
    issue_slug = slugify(record["issue_title"], 80)
    issue_dir = output_dir / f"vol40_no{issue_number:02d}_{issue_slug}"

    article_id = record.get("article_id") or "noid"
    title_slug = slugify(record["title"], 100)
    filename = f"{record['article_index_in_issue']:04d}_{article_id}_{title_slug}.pdf"
    path = issue_dir / filename
    rel_path = path.relative_to(output_dir.parent)
    return path, rel_path


def is_valid_pdf(path: Path) -> bool:
    if not path.exists() or path.stat().st_size < 8:
        return False
    with path.open("rb") as handle:
        return handle.read(4) == PDF_MAGIC


thread_local = threading.local()


def worker_session(verify_tls: bool) -> requests.Session:
    session = getattr(thread_local, "session", None)
    if session is None:
        session = make_session(verify_tls)
        thread_local.session = session
    return session


def download_one(
    record: dict[str, Any],
    output_dir: Path,
    force: bool,
    retries: int,
    timeout: int,
    verify_tls: bool,
) -> dict[str, Any]:
    output_path, rel_path = record_paths(record, output_dir)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    result = {
        "status": "unknown",
        "path": str(output_path),
        "relative_path": str(rel_path),
        "bytes": 0,
        "title": record["title"],
        "article_id": record.get("article_id", ""),
        "pdf_url": record["pdf_url"],
        "issue_number": record["issue_number"],
        "error": "",
    }

    if not force and is_valid_pdf(output_path):
        result["status"] = "skipped"
        result["bytes"] = output_path.stat().st_size
        return result

    tmp_path = output_path.with_suffix(output_path.suffix + ".part")
    session = worker_session(verify_tls)
    headers = {"Referer": record.get("issue_url") or record.get("page_url") or ARCHIVE_URL}

    last_error = ""
    for attempt in range(1, retries + 1):
        try:
            with session.get(
                record["pdf_url"],
                headers=headers,
                timeout=timeout,
                stream=True,
                allow_redirects=True,
            ) as response:
                response.raise_for_status()
                with tmp_path.open("wb") as handle:
                    for chunk in response.iter_content(chunk_size=1024 * 256):
                        if chunk:
                            handle.write(chunk)

            if not is_valid_pdf(tmp_path):
                preview = ""
                try:
                    preview = tmp_path.read_text(errors="replace")[:300]
                except Exception:
                    preview = "<binary non-pdf>"
                raise RuntimeError(f"downloaded file is not a PDF: {preview!r}")

            os.replace(tmp_path, output_path)
            result["status"] = "downloaded"
            result["bytes"] = output_path.stat().st_size
            return result
        except Exception as exc:  # noqa: BLE001 - report all per-record failures
            last_error = f"attempt {attempt}/{retries}: {type(exc).__name__}: {exc}"
            try:
                tmp_path.unlink()
            except FileNotFoundError:
                pass
            if attempt < retries:
                time.sleep(min(2**attempt, 10))

    result["status"] = "failed"
    result["error"] = last_error
    return result


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_manifest_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "issue_number",
        "issue_title",
        "article_index_in_issue",
        "article_id",
        "galley_id",
        "title",
        "authors",
        "pages",
        "page_url",
        "pdf_url",
        "local_path",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def validate_download_dir(output_dir: Path) -> dict[str, Any]:
    pdf_paths = sorted(output_dir.glob("**/*.pdf"))
    invalid = [str(path) for path in pdf_paths if not is_valid_pdf(path)]
    total_bytes = sum(path.stat().st_size for path in pdf_paths)
    return {
        "pdf_files": len(pdf_paths),
        "invalid_pdf_files": len(invalid),
        "invalid_paths": invalid[:100],
        "total_bytes": total_bytes,
    }


def main() -> int:
    args = build_parser().parse_args()
    if not args.verify_tls:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    output_dir = Path(args.output_dir)
    metadata_dir = Path(args.metadata_dir)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    print("Collecting AAAI 2026 issue list...", flush=True)
    session = make_session(args.verify_tls)
    issues = collect_issues(
        session,
        args.archive_url,
        args.archive_pages,
        args.timeout,
        args.scrape_retries,
    )
    write_json(metadata_dir / "issues.json", issues)
    print(f"Found {len(issues)} Vol. 40 issues.", flush=True)

    all_records: list[dict[str, Any]] = []
    for index, issue in enumerate(issues, start=1):
        records = parse_issue(session, issue, args.timeout, args.scrape_retries)
        all_records.extend(records)
        print(
            f"[{index:02d}/{len(issues):02d}] "
            f"issue {issue['issue_number']:02d}: {len(records)} PDFs",
            flush=True,
        )

    seen_pdf_urls: set[str] = set()
    deduped_records: list[dict[str, Any]] = []
    for record in all_records:
        if record["pdf_url"] in seen_pdf_urls:
            continue
        seen_pdf_urls.add(record["pdf_url"])
        output_path, rel_path = record_paths(record, output_dir)
        record["local_path"] = str(output_path)
        record["relative_local_path"] = str(rel_path)
        deduped_records.append(record)

    all_records = deduped_records
    write_json(metadata_dir / "manifest.json", all_records)
    write_jsonl(metadata_dir / "manifest.jsonl", all_records)
    write_manifest_csv(metadata_dir / "manifest.csv", all_records)
    print(f"Manifest contains {len(all_records)} unique PDF records.", flush=True)

    if args.list_only:
        summary = {
            "issues": len(issues),
            "pdf_records": len(all_records),
            "output_dir": str(output_dir),
            "metadata_dir": str(metadata_dir),
            "downloaded": 0,
            "skipped": 0,
            "failed": 0,
        }
        write_json(metadata_dir / "summary.json", summary)
        print(json.dumps(summary, indent=2), flush=True)
        return 0

    records_to_download = all_records[: args.limit] if args.limit else all_records
    results_path = metadata_dir / "download_results.jsonl"
    print(
        f"Downloading {len(records_to_download)} PDFs with {args.workers} workers...",
        flush=True,
    )

    counts = {"downloaded": 0, "skipped": 0, "failed": 0}
    results: list[dict[str, Any]] = []
    started = time.time()
    with results_path.open("w", encoding="utf-8") as results_file:
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, args.workers)) as executor:
            futures = [
                executor.submit(
                    download_one,
                    record,
                    output_dir,
                    args.force,
                    args.retries,
                    args.timeout,
                    args.verify_tls,
                )
                for record in records_to_download
            ]
            for done, future in enumerate(concurrent.futures.as_completed(futures), start=1):
                result = future.result()
                results.append(result)
                counts[result["status"]] = counts.get(result["status"], 0) + 1
                results_file.write(json.dumps(result, ensure_ascii=False) + "\n")
                results_file.flush()
                if done == 1 or done % 50 == 0 or done == len(records_to_download):
                    elapsed = time.time() - started
                    rate = done / elapsed if elapsed else 0
                    print(
                        f"{done}/{len(records_to_download)} complete "
                        f"(downloaded={counts.get('downloaded', 0)}, "
                        f"skipped={counts.get('skipped', 0)}, "
                        f"failed={counts.get('failed', 0)}, "
                        f"rate={rate:.2f}/s)",
                        flush=True,
                    )

    validation = validate_download_dir(output_dir)
    summary = {
        "issues": len(issues),
        "pdf_records": len(all_records),
        "attempted": len(records_to_download),
        "downloaded": counts.get("downloaded", 0),
        "skipped": counts.get("skipped", 0),
        "failed": counts.get("failed", 0),
        "output_dir": str(output_dir),
        "metadata_dir": str(metadata_dir),
        "results_path": str(results_path),
        "validation": validation,
    }
    write_json(metadata_dir / "summary.json", summary)
    print(json.dumps(summary, indent=2), flush=True)
    return 1 if counts.get("failed", 0) else 0


if __name__ == "__main__":
    raise SystemExit(main())
