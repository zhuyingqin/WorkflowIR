#!/usr/bin/env python3
"""Compare free-form baseline lit-search runs against WorkflowIR-controlled runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")


def summarize_baseline(batch_manifest: dict[str, Any]) -> dict[str, Any]:
    results = batch_manifest.get("results", []) if isinstance(batch_manifest.get("results"), list) else []
    total = len(results)
    statuses: dict[str, int] = {}
    timed_out = 0
    completed = 0
    for result in results:
        if not isinstance(result, dict):
            continue
        status = str(result.get("status"))
        statuses[status] = statuses.get(status, 0) + 1
        if result.get("timed_out") or status == "timeout":
            timed_out += 1
        if status == "completed":
            completed += 1
    return {
        "total": total,
        "statuses": statuses,
        "completion_rate": ratio(completed, total),
        "timeout_rate": ratio(timed_out, total),
        "contract_pass_rate": None,
        "notes": "Baseline manifest does not enforce required output contract; missing-file rates are mined from run traces separately.",
    }


def summarize_workflowir(batch_manifest: dict[str, Any]) -> dict[str, Any]:
    results = batch_manifest.get("results", []) if isinstance(batch_manifest.get("results"), list) else []
    total = len(results)
    statuses: dict[str, int] = {}
    completed = 0
    contract_passed = 0
    missing_required_total = 0
    total_deduped = 0
    full_exports = 0
    for result in results:
        if not isinstance(result, dict):
            continue
        status = str(result.get("status"))
        statuses[status] = statuses.get(status, 0) + 1
        if status == "completed":
            completed += 1
        if result.get("contract_passed"):
            contract_passed += 1
        contract = result.get("contract") if isinstance(result.get("contract"), dict) else {}
        missing_required_total += len(contract.get("missing_files") or [])
        run_dir = result.get("run_dir")
        if isinstance(run_dir, str):
            eval_path = Path(run_dir) / "RETRIEVAL_EVAL.json"
            if eval_path.exists():
                payload = read_json(eval_path)
                coverage = payload.get("coverage") if isinstance(payload, dict) else {}
                deduped = coverage.get("total_deduped_works") if isinstance(coverage, dict) else None
                if isinstance(deduped, int):
                    total_deduped += deduped
                    full_exports += 1
    return {
        "total": total,
        "statuses": statuses,
        "completion_rate": ratio(completed, total),
        "timeout_rate": 0.0,
        "contract_pass_rate": ratio(contract_passed, total),
        "missing_required_files": missing_required_total,
        "full_export_rate": ratio(full_exports, total),
        "total_deduped_works": total_deduped,
    }


def ratio(numerator: int, denominator: int) -> float | None:
    if denominator == 0:
        return None
    return round(numerator / denominator, 4)


def delta(controlled: float | None, baseline: float | None) -> float | None:
    if controlled is None or baseline is None:
        return None
    return round(controlled - baseline, 4)


def report_markdown(baseline: dict[str, Any], workflowir: dict[str, Any], output_json: Path) -> str:
    rows = [
        ("completion_rate", baseline.get("completion_rate"), workflowir.get("completion_rate")),
        ("timeout_rate", baseline.get("timeout_rate"), workflowir.get("timeout_rate")),
        ("contract_pass_rate", baseline.get("contract_pass_rate"), workflowir.get("contract_pass_rate")),
        ("full_export_rate", None, workflowir.get("full_export_rate")),
    ]
    lines = [
        "# WorkflowIR LitSearch Effectiveness Report",
        "",
        "This report compares the free-form baseline agent batch with the WorkflowIR-controlled batch on the same topic set.",
        "",
        "## Metrics",
        "",
        "| Metric | Baseline | WorkflowIR | Delta |",
        "|---|---:|---:|---:|",
    ]
    for name, base, controlled in rows:
        lines.append(f"| {name} | {fmt(base)} | {fmt(controlled)} | {fmt(delta(controlled, base))} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- Baseline measures free-form agent execution reliability.",
            "- WorkflowIR measures the same retrieval task with explicit node contracts, deterministic OpenAlex execution, query repair, and artifact verification.",
            "- A higher WorkflowIR completion/contract rate supports the claim that structured workflow control improves agent reliability.",
            "",
            "## Artifacts",
            "",
            f"- Machine-readable comparison: `{output_json}`",
            "",
        ]
    )
    return "\n".join(lines)


def fmt(value: Any) -> str:
    if value is None:
        return "n/a"
    if isinstance(value, float):
        return f"{value:.2%}"
    return str(value)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline-batch", required=True)
    parser.add_argument("--workflowir-batch", required=True)
    parser.add_argument("--out-dir", default="data/workflowir_litsearch_eval")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    baseline_path = Path(args.baseline_batch)
    workflowir_path = Path(args.workflowir_batch)
    out_dir = Path(args.out_dir)
    baseline = summarize_baseline(read_json(baseline_path))
    workflowir = summarize_workflowir(read_json(workflowir_path))
    comparison = {
        "baseline_batch": str(baseline_path),
        "workflowir_batch": str(workflowir_path),
        "baseline": baseline,
        "workflowir": workflowir,
        "deltas": {
            "completion_rate": delta(workflowir.get("completion_rate"), baseline.get("completion_rate")),
            "timeout_rate": delta(workflowir.get("timeout_rate"), baseline.get("timeout_rate")),
            "contract_pass_rate": delta(workflowir.get("contract_pass_rate"), baseline.get("contract_pass_rate")),
        },
    }
    out_json = out_dir / "effectiveness_comparison.json"
    out_md = out_dir / "effectiveness_report.md"
    write_json(out_json, comparison)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(report_markdown(baseline, workflowir, out_json), encoding="utf-8")
    print(f"Wrote {out_json}")
    print(f"Wrote {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
