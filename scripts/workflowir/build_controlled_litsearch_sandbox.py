#!/usr/bin/env python3
"""Build the first controlled sandbox dataset for literature-search agents.

The dataset is intentionally offline and synthetic. Each task exposes typed
tool contracts, controlled failure injection, and ground-truth attribution
labels so later Codex-Agent experiments can separate tool faults from agent
planning and recovery faults.
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path
from typing import Any


DATASET_ID = "controlled_sandbox_litsearch_v1"
DATASET_VERSION = "0.2.0"
DATASET_DATE = "2026-05-04"
DEFAULT_OUT_DIR = "data/controlled_sandbox/litsearch_v1"


def tool_specs() -> list[dict[str, Any]]:
    tools = [
        {
            "tool_id": "search_catalog",
            "description": "Search the offline scholarly catalog by query text and structured filters.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["query", "filters", "top_k"],
                "properties": {
                    "query": {"type": "string", "minLength": 1},
                    "filters": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "year_from": {"type": "integer", "minimum": 2020},
                            "year_to": {"type": "integer", "maximum": 2026},
                            "venues": {"type": "array", "items": {"type": "string"}},
                            "must_have_tags": {"type": "array", "items": {"type": "string"}},
                            "exclude_tags": {"type": "array", "items": {"type": "string"}},
                            "sources": {"type": "array", "items": {"enum": ["conference", "journal", "workshop", "arxiv"]}},
                        },
                    },
                    "top_k": {"type": "integer", "minimum": 1, "maximum": 20},
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["paper_ids", "scores", "diagnostics"],
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}},
                    "scores": {"type": "object"},
                    "diagnostics": {"type": "object"},
                },
            },
            "preconditions": [
                "query must be non-empty",
                "year_from must be less than or equal to year_to when both are provided",
                "all requested sources must be known catalog source types",
            ],
            "effects": [
                "sets state.last_search_results to the returned paper_ids",
                "records normalized_query and filter_digest in state.search_history",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "search_catalog.fm.recall_drop",
                    "description": "A matching paper is missing from results although it satisfies query and filters.",
                    "attribution_label": "tool.search_catalog.recall_drop",
                },
                {
                    "failure_mode_id": "search_catalog.fm.filter_leakage",
                    "description": "A paper violating structured filters appears in results.",
                    "attribution_label": "tool.search_catalog.filter_leakage",
                },
                {
                    "failure_mode_id": "search_catalog.fm.source_omission",
                    "description": "The tool silently omits one requested source or venue family.",
                    "attribution_label": "tool.search_catalog.source_omission",
                },
                {
                    "failure_mode_id": "search_catalog.fm.duplicate_results",
                    "description": "The same paper id appears more than once in ranked results.",
                    "attribution_label": "tool.search_catalog.duplicate_results",
                },
                {
                    "failure_mode_id": "search_catalog.fm.query_constraint_drop",
                    "description": "The search backend ignores a semantic constraint from the query text.",
                    "attribution_label": "tool.search_catalog.query_semantics",
                },
            ],
        },
        {
            "tool_id": "fetch_metadata",
            "description": "Return structured metadata for known paper ids.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paper_ids", "fields"],
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "fields": {
                        "type": "array",
                        "items": {
                            "enum": [
                                "title",
                                "authors",
                                "year",
                                "venue",
                                "source",
                                "doi",
                                "tags",
                                "datasets",
                                "method_family",
                            ]
                        },
                    },
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["records", "missing_ids"],
                "properties": {
                    "records": {"type": "array", "items": {"type": "object"}},
                    "missing_ids": {"type": "array", "items": {"type": "string"}},
                },
            },
            "preconditions": [
                "paper_ids must be non-empty",
                "every paper id should exist in the current corpus unless the task asks for seed repair",
                "fields must come from the allowed metadata field set",
            ],
            "effects": [
                "sets state.last_metadata_records",
                "adds missing ids to state.metadata_warnings",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "fetch_metadata.fm.stale_metadata",
                    "description": "A field reflects an older catalog snapshot.",
                    "attribution_label": "tool.fetch_metadata.stale_metadata",
                },
                {
                    "failure_mode_id": "fetch_metadata.fm.id_alias_collision",
                    "description": "Metadata for one id is returned under a different id.",
                    "attribution_label": "tool.fetch_metadata.id_alias_collision",
                },
                {
                    "failure_mode_id": "fetch_metadata.fm.partial_response",
                    "description": "A requested field is missing with no missing_ids warning.",
                    "attribution_label": "tool.fetch_metadata.partial_response",
                },
                {
                    "failure_mode_id": "fetch_metadata.fm.precondition_rejected",
                    "description": "The tool rejects unknown or empty ids according to its precondition.",
                    "attribution_label": "agent.precondition.invalid_tool_input",
                },
            ],
        },
        {
            "tool_id": "retrieve_abstract",
            "description": "Return abstracts and short evidence snippets for paper ids.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paper_id", "include_snippets"],
                "properties": {
                    "paper_id": {"type": "string", "minLength": 1},
                    "include_snippets": {"type": "boolean"},
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["paper_id", "abstract", "snippets"],
                "properties": {
                    "paper_id": {"type": "string"},
                    "abstract": {"type": "string"},
                    "snippets": {"type": "array", "items": {"type": "string"}},
                },
            },
            "preconditions": [
                "paper_id must exist in the corpus",
                "metadata should usually be fetched before abstract-level reasoning",
            ],
            "effects": [
                "sets state.last_abstract",
                "adds paper_id to state.abstracts_seen",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "retrieve_abstract.fm.abstract_swap",
                    "description": "The abstract text belongs to another paper id.",
                    "attribution_label": "tool.retrieve_abstract.abstract_swap",
                },
                {
                    "failure_mode_id": "retrieve_abstract.fm.truncated_abstract",
                    "description": "The abstract is cut before its evidence-bearing clauses.",
                    "attribution_label": "tool.retrieve_abstract.truncated_abstract",
                },
                {
                    "failure_mode_id": "retrieve_abstract.fm.unavailable_fulltext",
                    "description": "The tool reports that abstract/fulltext retrieval is unavailable.",
                    "attribution_label": "tool.retrieve_abstract.unavailable",
                },
            ],
        },
        {
            "tool_id": "filter_papers",
            "description": "Apply explicit inclusion and exclusion criteria to a candidate paper set.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paper_ids", "criteria"],
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "criteria": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "include_tags": {"type": "array", "items": {"type": "string"}},
                            "exclude_tags": {"type": "array", "items": {"type": "string"}},
                            "year_from": {"type": "integer"},
                            "year_to": {"type": "integer"},
                            "min_evidence_score": {"type": "number"},
                        },
                    },
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["accepted_ids", "rejected"],
                "properties": {
                    "accepted_ids": {"type": "array", "items": {"type": "string"}},
                    "rejected": {"type": "object"},
                },
            },
            "preconditions": [
                "paper_ids should come from search_catalog, citation_graph, or a validated user seed",
                "criteria must encode at least one include, exclude, or year constraint",
            ],
            "effects": [
                "sets state.last_filtered_results",
                "records accepted and rejected ids with reasons",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "filter_papers.fm.criterion_inversion",
                    "description": "The tool treats exclude criteria as include criteria or the reverse.",
                    "attribution_label": "tool.filter_papers.criterion_inversion",
                },
                {
                    "failure_mode_id": "filter_papers.fm.tag_normalization_error",
                    "description": "Equivalent tag variants are not normalized.",
                    "attribution_label": "tool.filter_papers.tag_normalization",
                },
                {
                    "failure_mode_id": "filter_papers.fm.off_by_one_year",
                    "description": "Boundary-year papers are incorrectly included or excluded.",
                    "attribution_label": "tool.filter_papers.year_boundary",
                },
            ],
        },
        {
            "tool_id": "citation_graph",
            "description": "Expand a seed set through synthetic citation edges.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["seed_ids", "direction", "depth"],
                "properties": {
                    "seed_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "direction": {"enum": ["references", "cited_by", "both"]},
                    "depth": {"type": "integer", "minimum": 1, "maximum": 2},
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["nodes", "edges"],
                "properties": {
                    "nodes": {"type": "array", "items": {"type": "string"}},
                    "edges": {"type": "array", "items": {"type": "object"}},
                },
            },
            "preconditions": [
                "seed_ids must exist in the corpus",
                "direction must be one of references, cited_by, or both",
            ],
            "effects": [
                "sets state.last_citation_graph",
                "records graph expansion parameters",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "citation_graph.fm.spurious_edge",
                    "description": "A non-existent citation edge is returned.",
                    "attribution_label": "tool.citation_graph.spurious_edge",
                },
                {
                    "failure_mode_id": "citation_graph.fm.missing_edge",
                    "description": "A real citation edge is omitted.",
                    "attribution_label": "tool.citation_graph.missing_edge",
                },
                {
                    "failure_mode_id": "citation_graph.fm.direction_flip",
                    "description": "References and cited_by directions are swapped.",
                    "attribution_label": "tool.citation_graph.direction_flip",
                },
            ],
        },
        {
            "tool_id": "compare_methods",
            "description": "Create a structured comparison table over selected papers.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paper_ids", "dimensions"],
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}, "minItems": 2},
                    "dimensions": {
                        "type": "array",
                        "items": {
                            "enum": [
                                "artifact_type",
                                "tool_contracts",
                                "preconditions",
                                "effects",
                                "failure_modes",
                                "metrics",
                                "limitations",
                                "recovery_strategy",
                            ]
                        },
                    },
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["columns", "rows"],
                "properties": {
                    "columns": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array", "items": {"type": "object"}},
                },
            },
            "preconditions": [
                "paper_ids must be known",
                "at least two papers are required",
                "dimensions must be supported comparison dimensions",
            ],
            "effects": [
                "sets state.last_comparison_table",
                "marks comparison dimensions as inspected",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "compare_methods.fm.hallucinated_dimension",
                    "description": "The table includes a dimension not requested or unsupported by evidence.",
                    "attribution_label": "tool.compare_methods.hallucinated_dimension",
                },
                {
                    "failure_mode_id": "compare_methods.fm.misaligned_rows",
                    "description": "Cells from one paper are shifted into another paper row.",
                    "attribution_label": "tool.compare_methods.row_alignment",
                },
                {
                    "failure_mode_id": "compare_methods.fm.missing_negative_evidence",
                    "description": "Known limitations are omitted from the comparison.",
                    "attribution_label": "tool.compare_methods.omitted_limitations",
                },
            ],
        },
        {
            "tool_id": "export_bibtex",
            "description": "Export selected papers to BibTeX-like references.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paper_ids", "deduplicate"],
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "deduplicate": {"type": "boolean"},
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["bibtex", "warnings"],
                "properties": {
                    "bibtex": {"type": "string"},
                    "warnings": {"type": "array", "items": {"type": "string"}},
                },
            },
            "preconditions": [
                "paper_ids must be known",
                "metadata must include title, authors, year, venue, and doi for stable export",
            ],
            "effects": [
                "sets state.last_bibtex_export",
                "records exported ids and warnings",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "export_bibtex.fm.field_corruption",
                    "description": "One bibliographic field differs from source metadata.",
                    "attribution_label": "tool.export_bibtex.field_corruption",
                },
                {
                    "failure_mode_id": "export_bibtex.fm.deduplication_loss",
                    "description": "Deduplication removes a distinct paper.",
                    "attribution_label": "tool.export_bibtex.deduplication_loss",
                },
                {
                    "failure_mode_id": "export_bibtex.fm.format_invalid",
                    "description": "The returned BibTeX is syntactically malformed.",
                    "attribution_label": "tool.export_bibtex.invalid_format",
                },
            ],
        },
        {
            "tool_id": "save_lit_report",
            "description": "Persist a structured literature-search report for evaluation.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["task_id", "sections", "cited_paper_ids"],
                "properties": {
                    "task_id": {"type": "string"},
                    "sections": {
                        "type": "object",
                        "additionalProperties": {"type": "string"},
                    },
                    "cited_paper_ids": {"type": "array", "items": {"type": "string"}},
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["report_id", "saved_sections", "warnings"],
                "properties": {
                    "report_id": {"type": "string"},
                    "saved_sections": {"type": "array", "items": {"type": "string"}},
                    "warnings": {"type": "array", "items": {"type": "string"}},
                },
            },
            "preconditions": [
                "task_id must match the active task",
                "all cited_paper_ids must be known or explicitly marked unresolved",
                "sections must include the task-required section names",
            ],
            "effects": [
                "sets state.saved_report_id",
                "records saved_sections for report completeness checking",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "save_lit_report.fm.partial_write",
                    "description": "The tool saves only a subset of provided sections.",
                    "attribution_label": "tool.save_lit_report.partial_write",
                },
                {
                    "failure_mode_id": "save_lit_report.fm.section_drop",
                    "description": "A required section is dropped without warning.",
                    "attribution_label": "tool.save_lit_report.section_drop",
                },
                {
                    "failure_mode_id": "save_lit_report.fm.citation_mismatch",
                    "description": "The saved report cites paper ids not present in cited_paper_ids.",
                    "attribution_label": "tool.save_lit_report.citation_mismatch",
                },
            ],
        },
    ]
    tools.extend(extra_tool_specs())
    return tools


def extra_tool_specs() -> list[dict[str, Any]]:
    return [
        {
            "tool_id": "synthesize_query",
            "description": "Generate structured query variants from a literature-search goal.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["goal", "required_terms", "forbidden_terms", "max_variants"],
                "properties": {
                    "goal": {"type": "string", "minLength": 1},
                    "required_terms": {"type": "array", "items": {"type": "string"}},
                    "forbidden_terms": {"type": "array", "items": {"type": "string"}},
                    "max_variants": {"type": "integer", "minimum": 1, "maximum": 8},
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["queries", "coverage_notes"],
                "properties": {
                    "queries": {"type": "array", "items": {"type": "object"}},
                    "coverage_notes": {"type": "array", "items": {"type": "string"}},
                },
            },
            "preconditions": [
                "goal must be non-empty",
                "required_terms should encode every hard user constraint",
                "forbidden_terms must not appear in generated query strings",
            ],
            "effects": [
                "sets state.last_query_variants",
                "records covered and uncovered required terms",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "synthesize_query.fm.constraint_loss",
                    "description": "A generated query drops a hard required term.",
                    "attribution_label": "tool.synthesize_query.constraint_loss",
                },
                {
                    "failure_mode_id": "synthesize_query.fm.synonym_drift",
                    "description": "A synonym expansion drifts into an unrelated topic.",
                    "attribution_label": "tool.synthesize_query.synonym_drift",
                },
                {
                    "failure_mode_id": "synthesize_query.fm.forbidden_term_leak",
                    "description": "A forbidden term appears in one generated query.",
                    "attribution_label": "tool.synthesize_query.forbidden_term_leak",
                },
            ],
        },
        {
            "tool_id": "rank_papers",
            "description": "Rank candidate papers by relevance, recency, and evidence strength.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paper_ids", "objective", "weights"],
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "objective": {"type": "string", "minLength": 1},
                    "weights": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "relevance": {"type": "number"},
                            "recency": {"type": "number"},
                            "evidence": {"type": "number"},
                            "diversity": {"type": "number"},
                        },
                    },
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["ranked_ids", "score_breakdown"],
                "properties": {
                    "ranked_ids": {"type": "array", "items": {"type": "string"}},
                    "score_breakdown": {"type": "object"},
                },
            },
            "preconditions": [
                "paper_ids must be unique",
                "weights must include at least one positive value",
                "paper_ids should have metadata available before ranking",
            ],
            "effects": [
                "sets state.last_ranked_results",
                "records score_breakdown for ranking audit",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "rank_papers.fm.score_flip",
                    "description": "The ranked order inverts the stated scoring objective.",
                    "attribution_label": "tool.rank_papers.score_flip",
                },
                {
                    "failure_mode_id": "rank_papers.fm.popularity_bias",
                    "description": "A less relevant paper is promoted because of a hidden popularity proxy.",
                    "attribution_label": "tool.rank_papers.popularity_bias",
                },
                {
                    "failure_mode_id": "rank_papers.fm.duplicate_input_not_rejected",
                    "description": "The tool accepts duplicate paper ids despite requiring unique candidates.",
                    "attribution_label": "tool.rank_papers.duplicate_input_not_rejected",
                },
            ],
        },
        {
            "tool_id": "extract_claims",
            "description": "Extract evidence-backed claims from abstracts and metadata.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["paper_ids", "claim_types"],
                "properties": {
                    "paper_ids": {"type": "array", "items": {"type": "string"}, "minItems": 1},
                    "claim_types": {
                        "type": "array",
                        "items": {"enum": ["artifact", "method", "metric", "limitation", "failure_mode", "dataset"]},
                    },
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["claims", "unsupported"],
                "properties": {
                    "claims": {"type": "array", "items": {"type": "object"}},
                    "unsupported": {"type": "array", "items": {"type": "object"}},
                },
            },
            "preconditions": [
                "abstracts should be retrieved before claim extraction",
                "claim_types must use the supported taxonomy",
            ],
            "effects": [
                "sets state.last_claims",
                "records unsupported claim candidates",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "extract_claims.fm.polarity_flip",
                    "description": "A limitation or negative result is extracted as a positive capability.",
                    "attribution_label": "tool.extract_claims.polarity_flip",
                },
                {
                    "failure_mode_id": "extract_claims.fm.unsupported_claim",
                    "description": "A claim is emitted without abstract or metadata support.",
                    "attribution_label": "tool.extract_claims.unsupported_claim",
                },
                {
                    "failure_mode_id": "extract_claims.fm.missing_limitation",
                    "description": "A limitation present in evidence is omitted.",
                    "attribution_label": "tool.extract_claims.missing_limitation",
                },
            ],
        },
        {
            "tool_id": "validate_workflow_ir",
            "description": "Validate a proposed WorkflowIR plan against tool contracts and task constraints.",
            "input_schema": {
                "type": "object",
                "additionalProperties": False,
                "required": ["task_id", "workflow", "checks"],
                "properties": {
                    "task_id": {"type": "string"},
                    "workflow": {"type": "object"},
                    "checks": {
                        "type": "array",
                        "items": {"enum": ["schema", "dataflow", "precondition", "effect", "budget", "safety"]},
                    },
                },
            },
            "output_schema": {
                "type": "object",
                "required": ["status", "diagnostics", "blocking_errors"],
                "properties": {
                    "status": {"enum": ["ready", "blocked", "warning"]},
                    "diagnostics": {"type": "array", "items": {"type": "object"}},
                    "blocking_errors": {"type": "array", "items": {"type": "object"}},
                },
            },
            "preconditions": [
                "workflow nodes must reference available tool ids",
                "checks must include at least schema or precondition",
                "task_id must match the active task",
            ],
            "effects": [
                "sets state.last_workflow_diagnostics",
                "blocks execution when blocking_errors is non-empty",
            ],
            "failure_modes": [
                {
                    "failure_mode_id": "validate_workflow_ir.fm.false_negative",
                    "description": "The validator misses a deterministic schema, dataflow, or precondition error.",
                    "attribution_label": "tool.validate_workflow_ir.false_negative",
                },
                {
                    "failure_mode_id": "validate_workflow_ir.fm.false_positive",
                    "description": "The validator blocks a valid workflow.",
                    "attribution_label": "tool.validate_workflow_ir.false_positive",
                },
                {
                    "failure_mode_id": "validate_workflow_ir.fm.mislocalized_error",
                    "description": "The diagnostic points to the wrong node or edge.",
                    "attribution_label": "tool.validate_workflow_ir.mislocalized_error",
                },
            ],
        },
    ]


def corpus() -> list[dict[str, Any]]:
    rows = [
        {
            "paper_id": "LIT-001",
            "title": "TraceBench: Instrumented Tool-Use Traces for Research Agents",
            "authors": ["Mina Hart", "Owen Zhao", "Priya Nair"],
            "year": 2026,
            "venue": "ICLR",
            "source": "conference",
            "doi": "10.0000/csl.2026.001",
            "tags": ["benchmark", "tool_use", "trace", "error_attribution", "research_agent"],
            "datasets": ["TraceBench-Research"],
            "method_family": "instrumented benchmark",
            "abstract": "TraceBench introduces controlled multi-tool traces for research agents. It annotates tool schemas, preconditions, effects, and injected faults so evaluators can separate retrieval failures from planning and recovery failures.",
            "citations": ["LIT-005", "LIT-007", "LIT-015"],
        },
        {
            "paper_id": "LIT-002",
            "title": "SchemaLens: Detecting JSON Schema Drift in LLM Tool Calls",
            "authors": ["Luca Mendes", "Yara Singh"],
            "year": 2025,
            "venue": "NeurIPS",
            "source": "conference",
            "doi": "10.0000/csl.2025.002",
            "tags": ["schema", "tool_use", "contract", "drift_detection"],
            "datasets": ["SchemaLens-Calls"],
            "method_family": "schema consistency checker",
            "abstract": "SchemaLens studies failures caused by schema drift between an agent prompt and an executable tool. It reports validators for input schemas and output schemas and highlights recovery prompts that ask agents to inspect contract violations.",
            "citations": ["LIT-015", "LIT-019"],
        },
        {
            "paper_id": "LIT-003",
            "title": "Grounded Scholar: Citation Verification with Retrieval-Augmented Agents",
            "authors": ["Noah Park", "Elena Voss", "Aditi Rao"],
            "year": 2025,
            "venue": "ACL",
            "source": "conference",
            "doi": "10.0000/csl.2025.003",
            "tags": ["citation_verification", "rag", "evidence", "literature_review"],
            "datasets": ["GroundedScholar-Cite"],
            "method_family": "retrieval-augmented verifier",
            "abstract": "Grounded Scholar verifies whether generated literature-review claims are supported by retrieved abstracts and citation snippets. It emphasizes evidence coverage, quote alignment, and unsupported-claim detection.",
            "citations": ["LIT-006", "LIT-009"],
        },
        {
            "paper_id": "LIT-004",
            "title": "OpenQuery: Transparent Literature Search Plans for Scientific Agents",
            "authors": ["Sara Kim", "Ivan Ortega"],
            "year": 2024,
            "venue": "EMNLP",
            "source": "conference",
            "doi": "10.0000/csl.2024.004",
            "tags": ["query_planning", "literature_search", "transparency", "research_agent"],
            "datasets": ["OpenQuery-Plans"],
            "method_family": "query planner",
            "abstract": "OpenQuery decomposes literature-search goals into auditable boolean queries and source filters. The paper shows that transparent query plans improve recall diagnosis when agent-generated searches miss a relevant subtopic.",
            "citations": ["LIT-008", "LIT-020"],
        },
        {
            "paper_id": "LIT-005",
            "title": "Failure Attribution in Multi-Step Tool-Augmented Reasoning",
            "authors": ["Helena Morris", "Ben Ahmed", "Carmen Li"],
            "year": 2026,
            "venue": "AAAI",
            "source": "conference",
            "doi": "10.0000/csl.2026.005",
            "tags": ["error_attribution", "tool_use", "failure_modes", "reasoning"],
            "datasets": ["AttributionGrid"],
            "method_family": "fault attribution taxonomy",
            "abstract": "This work proposes a taxonomy for attributing failures in multi-step tool-augmented reasoning. It distinguishes contract violations, tool runtime faults, state corruption, planning mistakes, and failed recovery after a visible fault.",
            "citations": ["LIT-007", "LIT-015", "LIT-019"],
        },
        {
            "paper_id": "LIT-006",
            "title": "PaperTrail: Auditing Evidence Chains in Automated Literature Reviews",
            "authors": ["Nadia Feld", "Thomas Wu"],
            "year": 2023,
            "venue": "JCDL",
            "source": "conference",
            "doi": "10.0000/csl.2023.006",
            "tags": ["evidence_chain", "literature_review", "audit", "citation_verification"],
            "datasets": ["PaperTrail-Audit"],
            "method_family": "evidence-chain audit",
            "abstract": "PaperTrail audits evidence chains in automated literature reviews by linking search queries, retrieved papers, extracted snippets, and final claims. Its central metric is whether each claim has a traceable evidence path.",
            "citations": ["LIT-009"],
        },
        {
            "paper_id": "LIT-007",
            "title": "ToolSandbox: Unit Tests for Agent APIs under Perturbations",
            "authors": ["Ravi Menon", "Qian Li"],
            "year": 2024,
            "venue": "ICLR Workshop",
            "source": "workshop",
            "doi": "10.0000/csl.2024.007",
            "tags": ["sandbox", "tool_use", "benchmark", "failure_injection", "api_testing"],
            "datasets": ["ToolSandbox-API"],
            "method_family": "controlled sandbox",
            "abstract": "ToolSandbox defines executable API unit tests for agents. Each tool has a schema, precondition, effect, and failure mode, allowing controlled perturbations such as schema mismatch, stale state, and partial writes.",
            "citations": ["LIT-015", "LIT-019"],
        },
        {
            "paper_id": "LIT-008",
            "title": "Recall First, Rank Later: Robust Query Expansion for Scholarly Search",
            "authors": ["Jae Lin", "Marta Rossi"],
            "year": 2025,
            "venue": "SIGIR",
            "source": "conference",
            "doi": "10.0000/csl.2025.008",
            "tags": ["query_expansion", "literature_search", "recall", "ranking"],
            "datasets": ["ScholarRecall-50"],
            "method_family": "query expansion",
            "abstract": "Recall First, Rank Later argues that scholarly agents should maximize recall before ranking. It gives expansion templates for synonyms, venue families, and citation-neighborhood repair after a search misses a known anchor paper.",
            "citations": ["LIT-004", "LIT-020"],
        },
        {
            "paper_id": "LIT-009",
            "title": "Hallucination-Aware Bibliography Generation for LLM Scientists",
            "authors": ["Olivia Chen", "Sam Reed"],
            "year": 2024,
            "venue": "ACL",
            "source": "conference",
            "doi": "10.0000/csl.2024.009",
            "tags": ["bibliography", "hallucination", "citation_verification", "literature_review"],
            "datasets": ["BibHallucination"],
            "method_family": "bibliography verifier",
            "abstract": "This paper evaluates bibliography generation by LLM scientists and identifies hallucinated titles, corrupted venues, and unsupported citations. It recommends metadata cross-checking before final report export.",
            "citations": ["LIT-006"],
        },
        {
            "paper_id": "LIT-010",
            "title": "Multi-Agent Debate for Systematic Review Screening",
            "authors": ["Wei Huang", "Isabel Grant"],
            "year": 2026,
            "venue": "KDD",
            "source": "conference",
            "doi": "10.0000/csl.2026.010",
            "tags": ["multi_agent", "systematic_review", "screening", "literature_review"],
            "datasets": ["ScreenDebate"],
            "method_family": "multi-agent screening",
            "abstract": "Multi-Agent Debate uses independent reviewer agents to screen systematic-review candidates. It targets literature-review workflows and measures disagreement, false exclusion, and evidence sufficiency.",
            "citations": ["LIT-003", "LIT-006"],
        },
        {
            "paper_id": "LIT-011",
            "title": "DedupeGraph: Entity Resolution for Scholarly Corpora",
            "authors": ["Anika Bose", "Felix Mayer"],
            "year": 2025,
            "venue": "CIKM",
            "source": "conference",
            "doi": "10.0000/csl.2025.011",
            "tags": ["deduplication", "entity_resolution", "scholarly_corpus", "metadata"],
            "datasets": ["DedupeGraph-Scholar"],
            "method_family": "entity resolution",
            "abstract": "DedupeGraph resolves duplicate scholarly records by combining title similarity, DOI agreement, and citation-neighborhood features. It is useful when search tools return duplicate or alias records.",
            "citations": ["LIT-009"],
        },
        {
            "paper_id": "LIT-012",
            "title": "Temporal Drift in Literature-Watch Agents",
            "authors": ["Kira Patel", "Jon Bell"],
            "year": 2026,
            "venue": "arXiv",
            "source": "arxiv",
            "doi": "10.0000/csl.2026.012",
            "tags": ["temporal_drift", "literature_watch", "freshness", "research_agent"],
            "datasets": ["LitWatch-Drift"],
            "method_family": "temporal audit",
            "abstract": "Temporal Drift studies scheduled literature-watch agents whose cached metadata lags behind current paper records. The benchmark injects stale years, stale venue names, and missing arXiv revisions.",
            "citations": ["LIT-004", "LIT-008"],
        },
        {
            "paper_id": "LIT-013",
            "title": "Planner-Critic Tool Use for Evidence-Seeking Agents",
            "authors": ["Mateo Cruz", "Leah Brooks"],
            "year": 2025,
            "venue": "ICML",
            "source": "conference",
            "doi": "10.0000/csl.2025.013",
            "tags": ["planner_critic", "tool_use", "evidence", "reasoning"],
            "datasets": ["EvidenceSeek"],
            "method_family": "planner-critic agent",
            "abstract": "Planner-Critic agents alternate between search planning and critique of gathered evidence. The critic flags missing preconditions and asks for additional retrieval when a conclusion lacks enough paper support.",
            "citations": ["LIT-003", "LIT-005"],
        },
        {
            "paper_id": "LIT-014",
            "title": "Negative Results for Autonomous Paper Recommendation Agents",
            "authors": ["Dina Walsh", "Oscar Vega"],
            "year": 2024,
            "venue": "CHI",
            "source": "conference",
            "doi": "10.0000/csl.2024.014",
            "tags": ["negative_results", "recommendation", "paper_recommender", "human_factors"],
            "datasets": ["ReviewerAssist-Neg"],
            "method_family": "user study",
            "abstract": "This negative-results study shows that autonomous paper recommendation agents often overfit user preferences and miss unfamiliar but relevant work. It is about recommendation rather than systematic review screening.",
            "citations": ["LIT-008"],
        },
        {
            "paper_id": "LIT-015",
            "title": "API-First Literature Mining with Typed Effects",
            "authors": ["Grace Liu", "Martin Hale"],
            "year": 2025,
            "venue": "FAccT",
            "source": "conference",
            "doi": "10.0000/csl.2025.015",
            "tags": ["typed_effects", "tool_contract", "literature_mining", "audit"],
            "datasets": ["TypedLitMine"],
            "method_family": "typed effect system",
            "abstract": "API-First Literature Mining represents literature-search actions as typed tool effects. It focuses on auditable state changes, provenance, and fairness concerns in automated screening pipelines.",
            "citations": ["LIT-006", "LIT-019"],
        },
        {
            "paper_id": "LIT-016",
            "title": "CiteGuard: Detecting Unsupported Claims in Generated Surveys",
            "authors": ["Peter Novak", "Asha Mehta"],
            "year": 2026,
            "venue": "ACL",
            "source": "conference",
            "doi": "10.0000/csl.2026.016",
            "tags": ["unsupported_claims", "citation_verification", "survey_generation", "evidence"],
            "datasets": ["CiteGuard-Survey"],
            "method_family": "claim verifier",
            "abstract": "CiteGuard detects unsupported claims in generated survey sections by comparing claim spans against retrieved abstracts. It reports false support, missing citation, and citation-title mismatch errors.",
            "citations": ["LIT-003", "LIT-009"],
        },
        {
            "paper_id": "LIT-017",
            "title": "ScholarFlow: End-to-End Workflow Automation for Review Papers",
            "authors": ["Avery Stone", "Nina Becker"],
            "year": 2023,
            "venue": "VLDB",
            "source": "conference",
            "doi": "10.0000/csl.2023.017",
            "tags": ["workflow_automation", "literature_review", "pipeline", "research_agent"],
            "datasets": ["ScholarFlow-Runs"],
            "method_family": "workflow system",
            "abstract": "ScholarFlow automates review-paper workflows from query generation through drafting. It emphasizes orchestration and throughput, with less attention to controlled error injection or attribution.",
            "citations": ["LIT-004", "LIT-006"],
        },
        {
            "paper_id": "LIT-018",
            "title": "Benchmark Leakage in Agentic Search Evaluation",
            "authors": ["Camille Roy", "Vikram Das"],
            "year": 2026,
            "venue": "NeurIPS",
            "source": "conference",
            "doi": "10.0000/csl.2026.018",
            "tags": ["benchmark", "leakage", "agentic_search", "evaluation", "failure_modes"],
            "datasets": ["LeakageProbe"],
            "method_family": "benchmark audit",
            "abstract": "Benchmark Leakage analyzes how agentic search benchmarks leak target paper titles into prompts or tool observations. It proposes hidden-target splits and perturbation checks for search evaluation.",
            "citations": ["LIT-001", "LIT-007"],
        },
        {
            "paper_id": "LIT-019",
            "title": "Robust Precondition Checking for Tool-Augmented Agents",
            "authors": ["Iris Morgan", "Ken Sato"],
            "year": 2025,
            "venue": "OOPSLA",
            "source": "conference",
            "doi": "10.0000/csl.2025.019",
            "tags": ["preconditions", "tool_contract", "programming_languages", "tool_use"],
            "datasets": ["PreconditionSuite"],
            "method_family": "precondition checker",
            "abstract": "Robust Precondition Checking formalizes executable preconditions for tool-augmented agents. It shows that invalid seeds, missing required fields, and wrong call order should be attributed to agent-side input validation when tools reject them correctly.",
            "citations": ["LIT-015"],
        },
        {
            "paper_id": "LIT-020",
            "title": "SearchSieve: Progressive Pruning for Scholarly Retrieval",
            "authors": ["Renee Alonzo", "Hugo Klein"],
            "year": 2024,
            "venue": "SIGIR",
            "source": "conference",
            "doi": "10.0000/csl.2024.020",
            "tags": ["progressive_pruning", "literature_search", "retrieval", "screening"],
            "datasets": ["SearchSieve-Queries"],
            "method_family": "progressive retrieval",
            "abstract": "SearchSieve starts with broad recall-oriented retrieval and progressively prunes results using explicit inclusion and exclusion criteria. It reports when pruning decisions remove relevant papers.",
            "citations": ["LIT-004"],
        },
    ]
    return rows


def attribution_taxonomy() -> dict[str, Any]:
    return {
        "taxonomy_id": "controlled_sandbox_attribution_v1",
        "root_causes": [
            {
                "root_cause": "tool_contract_violation",
                "definition": "The tool violates its declared schema, precondition behavior, or output contract.",
            },
            {
                "root_cause": "tool_effect_fault",
                "definition": "The tool returns plausible output but corrupts state or fails to realize its declared effect.",
            },
            {
                "root_cause": "tool_retrieval_fault",
                "definition": "The search or retrieval tool misses, leaks, swaps, duplicates, or corrupts scholarly evidence.",
            },
            {
                "root_cause": "agent_precondition_violation",
                "definition": "The agent calls a tool with invalid inputs or wrong call order despite visible preconditions.",
            },
            {
                "root_cause": "agent_constraint_loss",
                "definition": "The agent drops a user constraint while planning, filtering, or writing the final answer.",
            },
            {
                "root_cause": "agent_recovery_failure",
                "definition": "A visible tool fault occurs, but the agent fails to cross-check or recover.",
            },
        ],
        "labels": [
            "clean.no_injected_fault",
            "tool.search_catalog.recall_drop",
            "tool.search_catalog.filter_leakage",
            "tool.search_catalog.source_omission",
            "tool.search_catalog.duplicate_results",
            "tool.search_catalog.query_semantics",
            "tool.fetch_metadata.stale_metadata",
            "tool.fetch_metadata.id_alias_collision",
            "tool.fetch_metadata.partial_response",
            "tool.retrieve_abstract.abstract_swap",
            "tool.retrieve_abstract.truncated_abstract",
            "tool.filter_papers.criterion_inversion",
            "tool.citation_graph.spurious_edge",
            "tool.citation_graph.missing_edge",
            "tool.citation_graph.direction_flip",
            "tool.compare_methods.hallucinated_dimension",
            "tool.compare_methods.row_alignment",
            "tool.compare_methods.omitted_limitations",
            "tool.export_bibtex.field_corruption",
            "tool.export_bibtex.deduplication_loss",
            "tool.export_bibtex.invalid_format",
            "tool.save_lit_report.partial_write",
            "tool.save_lit_report.section_drop",
            "tool.save_lit_report.citation_mismatch",
            "tool.synthesize_query.constraint_loss",
            "tool.synthesize_query.synonym_drift",
            "tool.synthesize_query.forbidden_term_leak",
            "tool.rank_papers.score_flip",
            "tool.rank_papers.popularity_bias",
            "tool.rank_papers.duplicate_input_not_rejected",
            "tool.extract_claims.polarity_flip",
            "tool.extract_claims.unsupported_claim",
            "tool.extract_claims.missing_limitation",
            "tool.validate_workflow_ir.false_negative",
            "tool.validate_workflow_ir.false_positive",
            "tool.validate_workflow_ir.mislocalized_error",
            "agent.precondition.invalid_tool_input",
            "agent.constraint_loss",
            "agent.recovery_failure",
        ],
    }


def make_task(
    task_id: str,
    split: str,
    title: str,
    user_prompt: str,
    available_tools: list[str],
    must_include: list[str],
    must_exclude: list[str],
    required_facets: list[str],
    trace: list[dict[str, Any]],
    injections: list[dict[str, Any]] | None = None,
    level: int = 1,
) -> dict[str, Any]:
    labels = ["clean.no_injected_fault"] if not injections else [item["ground_truth_attribution"] for item in injections]
    return {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "task_id": task_id,
        "split": split,
        "level": level,
        "title": title,
        "category": "literature_search_controlled_sandbox",
        "user_prompt": user_prompt,
        "available_tools": available_tools,
        "initial_state": {
            "current_date": DATASET_DATE,
            "corpus_snapshot": "synthetic_litsearch_corpus_v1",
            "known_paper_ids": [],
            "notes": "Offline synthetic corpus. The agent should reason from tool observations only.",
        },
        "success_criteria": [
            "satisfy the user prompt constraints",
            "cite paper ids from the corpus for every substantive claim",
            "when observations conflict, identify the most likely fault source before finalizing",
        ],
        "oracle": {
            "must_include_paper_ids": must_include,
            "must_exclude_paper_ids": must_exclude,
            "required_answer_facets": required_facets,
            "ground_truth_attribution_labels": labels,
        },
        "expected_trace": trace,
        "injections": injections or [],
    }


def inj(
    injection_id: str,
    target_tool: str,
    failure_mode_id: str,
    trigger: dict[str, Any],
    injected_behavior: str,
    ground_truth_attribution: str,
    observable_symptoms: list[str],
    recovery_hint: str,
    severity: str = "medium",
) -> dict[str, Any]:
    return {
        "injection_id": injection_id,
        "target_tool": target_tool,
        "failure_mode_id": failure_mode_id,
        "trigger": trigger,
        "injected_behavior": injected_behavior,
        "ground_truth_attribution": ground_truth_attribution,
        "observable_symptoms": observable_symptoms,
        "recovery_hint": recovery_hint,
        "severity": severity,
    }


def step(number: int, tool_id: str, purpose: str, expected_effect: str) -> dict[str, Any]:
    return {
        "step": number,
        "tool_id": tool_id,
        "purpose": purpose,
        "expected_effect": expected_effect,
    }


def tasks() -> list[dict[str, Any]]:
    common_report_tools = [
        "search_catalog",
        "fetch_metadata",
        "retrieve_abstract",
        "filter_papers",
        "compare_methods",
        "save_lit_report",
    ]
    rows = [
        make_task(
            task_id="CLS-LIT-001",
            split="dev",
            level=1,
            title="Clean benchmark and sandbox retrieval",
            user_prompt=(
                "Find 3-4 papers from 2024 onward that introduce benchmarks, sandboxes, "
                "or controlled evaluations for tool-using research agents. Summarize the "
                "artifact each paper contributes and the failure modes it can expose."
            ),
            available_tools=common_report_tools,
            must_include=["LIT-001", "LIT-007", "LIT-018"],
            must_exclude=["LIT-017"],
            required_facets=["artifact_type", "failure_modes", "year_filter_2024_onward"],
            trace=[
                step(1, "search_catalog", "retrieve benchmark/sandbox candidates", "candidate ids contain LIT-001, LIT-007, LIT-018"),
                step(2, "fetch_metadata", "check year and venue constraints", "metadata confirms all included papers are 2024 or newer"),
                step(3, "retrieve_abstract", "verify artifact and failure-mode claims", "abstract snippets support each comparison row"),
                step(4, "compare_methods", "compare artifacts and failure modes", "table covers artifact_type and failure_modes"),
                step(5, "save_lit_report", "save final controlled search report", "all requested sections are saved"),
            ],
        ),
        make_task(
            task_id="CLS-LIT-002",
            split="train",
            level=1,
            title="Recall-drop attribution in benchmark search",
            user_prompt=(
                "Search for 2024-2026 benchmark papers about agentic literature search and "
                "tool-use evaluation. If a known benchmark family seems absent, repair the "
                "search with query expansion or citation-neighborhood checks."
            ),
            available_tools=["search_catalog", "fetch_metadata", "citation_graph", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-001", "LIT-007", "LIT-018"],
            must_exclude=["LIT-014"],
            required_facets=["recall_check", "fault_attribution", "repair_action"],
            trace=[
                step(1, "search_catalog", "run initial benchmark search", "initial result set should expose missing benchmark-leakage paper under injection"),
                step(2, "citation_graph", "expand from LIT-001 or LIT-007", "citation graph recovers LIT-018"),
                step(3, "fetch_metadata", "validate recovered candidate", "metadata confirms LIT-018 is a 2026 benchmark paper"),
                step(4, "save_lit_report", "save attribution and recovered set", "report labels search recall-drop fault"),
            ],
            injections=[
                inj(
                    injection_id="INJ-SEARCH-RECALL-001",
                    target_tool="search_catalog",
                    failure_mode_id="search_catalog.fm.recall_drop",
                    trigger={"query_contains_any": ["benchmark", "agentic search"], "year_from": 2024},
                    injected_behavior="Omit LIT-018 from the initial ranked search results despite matching tags and filters.",
                    ground_truth_attribution="tool.search_catalog.recall_drop",
                    observable_symptoms=[
                        "LIT-001 cites LIT-018 but search did not return it",
                        "LIT-018 metadata satisfies the same filters when fetched later",
                    ],
                    recovery_hint="Use citation_graph from returned benchmark papers or broaden query with leakage/evaluation synonyms.",
                    severity="high",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-003",
            split="train",
            level=1,
            title="Stale metadata in literature-watch seeds",
            user_prompt=(
                "Build a May 2026 literature-watch seed list for papers from 2026 about "
                "temporal drift, freshness, or benchmark leakage in research-agent search. "
                "Flag any metadata inconsistency you detect."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-012", "LIT-018"],
            must_exclude=["LIT-004", "LIT-008"],
            required_facets=["freshness", "metadata_consistency", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "find freshness and leakage papers in 2026", "candidate ids include LIT-012 and LIT-018"),
                step(2, "fetch_metadata", "validate years and sources", "metadata conflict is visible for LIT-012 under injection"),
                step(3, "retrieve_abstract", "cross-check stale year against abstract topic", "abstract confirms temporal drift benchmark context"),
                step(4, "save_lit_report", "save seed list and inconsistency note", "report attributes stale year to metadata tool"),
            ],
            injections=[
                inj(
                    injection_id="INJ-META-STALE-001",
                    target_tool="fetch_metadata",
                    failure_mode_id="fetch_metadata.fm.stale_metadata",
                    trigger={"paper_ids_contains": "LIT-012", "fields_contains": "year"},
                    injected_behavior="Return year=2025 for LIT-012 while the corpus oracle has year=2026.",
                    ground_truth_attribution="tool.fetch_metadata.stale_metadata",
                    observable_symptoms=[
                        "search filter year_from=2026 returned LIT-012",
                        "fetch_metadata reports LIT-012 as 2025",
                    ],
                    recovery_hint="Compare the search diagnostics, abstract, and metadata; do not silently drop LIT-012.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-004",
            split="test",
            level=2,
            title="Abstract-swap attribution in citation verification",
            user_prompt=(
                "Find ACL papers on citation verification or unsupported-claim detection for generated "
                "surveys. Explain the difference between bibliography hallucination, citation verification, "
                "and unsupported-claim detection."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "compare_methods", "save_lit_report"],
            must_include=["LIT-003", "LIT-009", "LIT-016"],
            must_exclude=["LIT-006"],
            required_facets=["citation_verification", "unsupported_claims", "abstract_metadata_crosscheck"],
            trace=[
                step(1, "search_catalog", "find ACL citation papers", "candidate ids include LIT-003, LIT-009, LIT-016"),
                step(2, "fetch_metadata", "check venue and titles", "metadata confirms ACL papers"),
                step(3, "retrieve_abstract", "read abstracts for distinctions", "injected abstract swap creates title/abstract mismatch"),
                step(4, "compare_methods", "compare claim and citation failure types", "comparison separates bibliography, citation, and claim-support errors"),
                step(5, "save_lit_report", "save final distinction and attribution", "report notes retrieve_abstract swap"),
            ],
            injections=[
                inj(
                    injection_id="INJ-ABSTRACT-SWAP-001",
                    target_tool="retrieve_abstract",
                    failure_mode_id="retrieve_abstract.fm.abstract_swap",
                    trigger={"paper_id": "LIT-003", "include_snippets": True},
                    injected_behavior="Return the abstract and snippets for LIT-016 while preserving paper_id=LIT-003.",
                    ground_truth_attribution="tool.retrieve_abstract.abstract_swap",
                    observable_symptoms=[
                        "abstract text discusses generated surveys and unsupported claims",
                        "metadata title for LIT-003 says Grounded Scholar",
                    ],
                    recovery_hint="Cross-check title-specific terms before using abstract evidence.",
                    severity="high",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-005",
            split="train",
            level=1,
            title="Filter inversion during systematic-review screening",
            user_prompt=(
                "Identify papers about agent-assisted systematic-review or literature-review screening. "
                "Exclude papers that are only paper recommendation or broad workflow automation systems."
            ),
            available_tools=["search_catalog", "fetch_metadata", "filter_papers", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-006", "LIT-010", "LIT-020"],
            must_exclude=["LIT-014", "LIT-017"],
            required_facets=["screening_vs_recommendation", "filter_reasoning", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve review-screening and workflow candidates", "candidate set includes true and distractor papers"),
                step(2, "filter_papers", "exclude recommendation and workflow-only papers", "under injection, excluded tags are incorrectly accepted"),
                step(3, "fetch_metadata", "inspect accepted and rejected records", "metadata reveals LIT-014 or LIT-017 violates prompt constraints"),
                step(4, "save_lit_report", "save corrected accepted set", "report attributes bad accepted ids to filter inversion"),
            ],
            injections=[
                inj(
                    injection_id="INJ-FILTER-INVERT-001",
                    target_tool="filter_papers",
                    failure_mode_id="filter_papers.fm.criterion_inversion",
                    trigger={"exclude_tags_contains_any": ["recommendation", "workflow_automation"]},
                    injected_behavior="Return LIT-014 and LIT-017 as accepted even though their exclusion tags match.",
                    ground_truth_attribution="tool.filter_papers.criterion_inversion",
                    observable_symptoms=[
                        "accepted_ids include papers with excluded tags",
                        "rejected reasons contradict the criteria",
                    ],
                    recovery_hint="Audit accepted ids against fetched metadata tags before finalizing.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-006",
            split="test",
            level=2,
            title="Spurious citation edge in query-expansion repair",
            user_prompt=(
                "Starting from query-expansion work, trace backward to evidence-chain auditing papers "
                "that would help repair missed literature-search results. Ignore unrelated typed-effect papers "
                "unless the citation path is real."
            ),
            available_tools=["search_catalog", "citation_graph", "fetch_metadata", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-004", "LIT-006", "LIT-008", "LIT-020"],
            must_exclude=["LIT-015"],
            required_facets=["citation_path_validity", "evidence_chain", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "find query expansion papers", "candidate ids include LIT-004, LIT-008, LIT-020"),
                step(2, "citation_graph", "expand references and cited_by links", "injected graph contains a spurious LIT-008 -> LIT-015 edge"),
                step(3, "fetch_metadata", "inspect graph neighbors", "metadata shows LIT-015 is typed effects, not evidence-chain repair"),
                step(4, "retrieve_abstract", "confirm relevant evidence-chain papers", "abstracts support LIT-006 and exclude LIT-015"),
                step(5, "save_lit_report", "save graph-based repair explanation", "report attributes LIT-015 path to citation_graph spurious edge"),
            ],
            injections=[
                inj(
                    injection_id="INJ-GRAPH-SPURIOUS-001",
                    target_tool="citation_graph",
                    failure_mode_id="citation_graph.fm.spurious_edge",
                    trigger={"seed_ids_contains": "LIT-008", "direction": "both"},
                    injected_behavior="Add a false edge LIT-008 -> LIT-015 to the returned citation graph.",
                    ground_truth_attribution="tool.citation_graph.spurious_edge",
                    observable_symptoms=[
                        "LIT-008 corpus citations do not include LIT-015",
                        "LIT-015 topic tags do not match evidence-chain repair",
                    ],
                    recovery_hint="Validate surprising graph edges against metadata and abstracts.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-007",
            split="dev",
            level=1,
            title="BibTeX field corruption for tool-contract papers",
            user_prompt=(
                "Prepare an annotated bibliography for papers about schema drift, typed effects, "
                "and precondition checking in tool-augmented agents. Include stable paper ids and detect "
                "any corrupted bibliographic fields."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "export_bibtex", "save_lit_report"],
            must_include=["LIT-002", "LIT-015", "LIT-019"],
            must_exclude=["LIT-014"],
            required_facets=["tool_contracts", "bibtex_crosscheck", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "find tool-contract papers", "candidate ids include LIT-002, LIT-015, LIT-019"),
                step(2, "fetch_metadata", "collect stable metadata", "metadata provides source DOI values"),
                step(3, "export_bibtex", "export references", "injected export corrupts one DOI field"),
                step(4, "save_lit_report", "save annotated bibliography with warnings", "report attributes mismatch to export_bibtex"),
            ],
            injections=[
                inj(
                    injection_id="INJ-BIB-FIELD-001",
                    target_tool="export_bibtex",
                    failure_mode_id="export_bibtex.fm.field_corruption",
                    trigger={"paper_ids_contains": "LIT-002"},
                    injected_behavior="Emit doi={10.0000/csl.2024.002} for LIT-002 instead of 10.0000/csl.2025.002.",
                    ground_truth_attribution="tool.export_bibtex.field_corruption",
                    observable_symptoms=[
                        "fetch_metadata DOI and exported DOI disagree",
                        "only the exported BibTeX field is inconsistent",
                    ],
                    recovery_hint="Compare exported references against fetched metadata before saving.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-008",
            split="test",
            level=2,
            title="Hallucinated comparison dimension",
            user_prompt=(
                "Compare papers that explicitly discuss schemas, preconditions, effects, or failure modes "
                "for tool-using agents. Use only the dimensions supported by tool contracts and abstracts."
            ),
            available_tools=common_report_tools,
            must_include=["LIT-001", "LIT-002", "LIT-005", "LIT-007", "LIT-015", "LIT-019"],
            must_exclude=["LIT-014"],
            required_facets=["schema", "preconditions", "effects", "failure_modes", "unsupported_dimension_detection"],
            trace=[
                step(1, "search_catalog", "find contract and attribution papers", "candidate ids cover all contract dimensions"),
                step(2, "fetch_metadata", "validate metadata and tags", "metadata confirms contract-related tags"),
                step(3, "retrieve_abstract", "collect evidence for dimensions", "abstract evidence supports only requested dimensions"),
                step(4, "compare_methods", "build comparison table", "injected table includes unsupported dimension"),
                step(5, "save_lit_report", "save corrected comparison", "report flags unsupported comparison dimension"),
            ],
            injections=[
                inj(
                    injection_id="INJ-COMPARE-DIM-001",
                    target_tool="compare_methods",
                    failure_mode_id="compare_methods.fm.hallucinated_dimension",
                    trigger={"dimensions_contains": "failure_modes"},
                    injected_behavior="Add an unsupported column named human_eye_tracking_score with invented values.",
                    ground_truth_attribution="tool.compare_methods.hallucinated_dimension",
                    observable_symptoms=[
                        "column was not requested",
                        "no abstract or metadata field supports the column",
                    ],
                    recovery_hint="Drop unsupported columns and attribute the issue to compare_methods.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-009",
            split="train",
            level=1,
            title="Source omission in ACL citation search",
            user_prompt=(
                "Find ACL papers on bibliography hallucination, citation verification, or unsupported "
                "claims in generated literature reviews. Explain why each selected paper belongs in the set."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "citation_graph", "save_lit_report"],
            must_include=["LIT-003", "LIT-009", "LIT-016"],
            must_exclude=["LIT-006"],
            required_facets=["acl_filter", "source_coverage_check", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "run ACL citation search", "injected results omit one ACL source family or title family"),
                step(2, "citation_graph", "repair from returned ACL papers", "citation graph can recover omitted ACL neighbor"),
                step(3, "fetch_metadata", "validate recovered ACL papers", "metadata confirms all three are ACL"),
                step(4, "save_lit_report", "save selected set and source-omission note", "report labels source omission if observed"),
            ],
            injections=[
                inj(
                    injection_id="INJ-SEARCH-SOURCE-001",
                    target_tool="search_catalog",
                    failure_mode_id="search_catalog.fm.source_omission",
                    trigger={"venues_contains": "ACL"},
                    injected_behavior="Return LIT-003 and LIT-016 but omit LIT-009 for ACL bibliography hallucination searches.",
                    ground_truth_attribution="tool.search_catalog.source_omission",
                    observable_symptoms=[
                        "LIT-003 cites LIT-009",
                        "LIT-009 metadata venue is ACL and tags match the query",
                    ],
                    recovery_hint="Use citation_graph or synonym search for bibliography hallucination.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-010",
            split="dev",
            level=1,
            title="Partial report write after successful retrieval",
            user_prompt=(
                "Create and save a concise literature report with exactly these sections: Search Plan, "
                "Selected Papers, Risks, and Next Dataset Ideas. Use papers about controlled tool-use "
                "sandboxes and attribution."
            ),
            available_tools=common_report_tools,
            must_include=["LIT-001", "LIT-005", "LIT-007"],
            must_exclude=["LIT-014"],
            required_facets=["required_sections", "saved_section_check", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "find sandbox and attribution papers", "candidate ids include LIT-001, LIT-005, LIT-007"),
                step(2, "fetch_metadata", "validate papers", "metadata supports final citations"),
                step(3, "retrieve_abstract", "collect evidence for report", "abstracts support risks and dataset ideas"),
                step(4, "save_lit_report", "save four required sections", "injected save omits Risks section"),
            ],
            injections=[
                inj(
                    injection_id="INJ-REPORT-PARTIAL-001",
                    target_tool="save_lit_report",
                    failure_mode_id="save_lit_report.fm.partial_write",
                    trigger={"sections_contains": "Risks"},
                    injected_behavior="Return saved_sections without Risks even though the input sections included it.",
                    ground_truth_attribution="tool.save_lit_report.partial_write",
                    observable_symptoms=[
                        "save_lit_report output lacks a required section",
                        "the missing section was present in the tool input",
                    ],
                    recovery_hint="Check saved_sections and retry or report the partial write.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-011",
            split="test",
            level=2,
            title="Invalid seed id as agent precondition violation",
            user_prompt=(
                "The seed list contains LIT-999 and LIT-002. Verify the schema-drift paper and repair "
                "invalid seeds before using them in a final bibliography."
            ),
            available_tools=["fetch_metadata", "search_catalog", "retrieve_abstract", "export_bibtex", "save_lit_report"],
            must_include=["LIT-002"],
            must_exclude=["LIT-999"],
            required_facets=["invalid_seed_repair", "precondition_reasoning", "fault_attribution"],
            trace=[
                step(1, "fetch_metadata", "attempt or avoid invalid seed fetch", "tool precondition rejection for LIT-999 is correct if called"),
                step(2, "search_catalog", "repair invalid seed by title/topic search", "search recovers LIT-002 only"),
                step(3, "retrieve_abstract", "verify schema-drift paper", "abstract confirms schema drift topic"),
                step(4, "export_bibtex", "export repaired bibliography", "bibliography excludes invalid seed"),
                step(5, "save_lit_report", "save repair note", "report attributes invalid seed to agent/input precondition, not tool fault"),
            ],
            injections=[
                inj(
                    injection_id="INJ-PRECONDITION-001",
                    target_tool="fetch_metadata",
                    failure_mode_id="fetch_metadata.fm.precondition_rejected",
                    trigger={"paper_ids_contains": "LIT-999"},
                    injected_behavior="Reject the call with missing_ids=['LIT-999'] and no metadata record for the invalid id.",
                    ground_truth_attribution="agent.precondition.invalid_tool_input",
                    observable_symptoms=[
                        "the tool behaves according to its precondition",
                        "the invalid id came from the task seed, not the corpus",
                    ],
                    recovery_hint="Search by topic/title and exclude the invalid seed from final output.",
                    severity="low",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-012",
            split="test",
            level=1,
            title="Duplicate search results in unique-paper selection",
            user_prompt=(
                "Return exactly five unique papers from 2024 onward that are most relevant to building a "
                "controlled literature-search sandbox. Deduplicate results before comparing methods."
            ),
            available_tools=common_report_tools,
            must_include=["LIT-001", "LIT-004", "LIT-005", "LIT-007", "LIT-018"],
            must_exclude=["LIT-001_DUPLICATE"],
            required_facets=["unique_count_5", "deduplication", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve controlled sandbox candidates", "injected results contain duplicate LIT-001"),
                step(2, "fetch_metadata", "validate unique ids", "metadata has one record for LIT-001"),
                step(3, "filter_papers", "deduplicate and enforce 2024 onward", "accepted ids contain five unique papers"),
                step(4, "compare_methods", "compare selected methods", "comparison uses unique rows only"),
                step(5, "save_lit_report", "save final unique set", "report labels duplicate search result"),
            ],
            injections=[
                inj(
                    injection_id="INJ-SEARCH-DUP-001",
                    target_tool="search_catalog",
                    failure_mode_id="search_catalog.fm.duplicate_results",
                    trigger={"query_contains_any": ["controlled", "sandbox"], "top_k": 6},
                    injected_behavior="Return ['LIT-001', 'LIT-007', 'LIT-001', 'LIT-005', 'LIT-004', 'LIT-018'] for a top_k=6 call.",
                    ground_truth_attribution="tool.search_catalog.duplicate_results",
                    observable_symptoms=[
                        "same paper id appears twice in paper_ids",
                        "unique result count is lower than returned result count",
                    ],
                    recovery_hint="Deduplicate before filtering and comparison.",
                    severity="low",
                )
            ],
        ),
    ]
    rows.extend(additional_tasks(common_report_tools))
    return rows


def additional_tasks(common_report_tools: list[str]) -> list[dict[str, Any]]:
    workflow_tools = common_report_tools + ["synthesize_query", "rank_papers", "extract_claims", "validate_workflow_ir"]
    return [
        make_task(
            task_id="CLS-LIT-013",
            split="train",
            level=1,
            title="Query synthesis loses hard schema constraint",
            user_prompt=(
                "Generate search queries for papers that explicitly mention schema or typed contracts. "
                "Do not include recommendation-only agents, then retrieve and summarize the relevant papers."
            ),
            available_tools=["synthesize_query", "search_catalog", "fetch_metadata", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-002", "LIT-015", "LIT-019"],
            must_exclude=["LIT-014"],
            required_facets=["query_constraints", "schema_or_contract", "fault_attribution"],
            trace=[
                step(1, "synthesize_query", "create schema/contract query variants", "injected query variants drop the schema constraint"),
                step(2, "search_catalog", "run corrected query variants", "results include LIT-002, LIT-015, LIT-019"),
                step(3, "fetch_metadata", "validate tags and years", "metadata confirms contract-related papers"),
                step(4, "save_lit_report", "save query loss diagnosis", "report attributes dropped term to synthesize_query"),
            ],
            injections=[
                inj(
                    injection_id="INJ-QUERY-CONSTRAINT-001",
                    target_tool="synthesize_query",
                    failure_mode_id="synthesize_query.fm.constraint_loss",
                    trigger={"required_terms_contains": "schema"},
                    injected_behavior="Generate variants about generic tool use but omit schema and typed contract terms.",
                    ground_truth_attribution="tool.synthesize_query.constraint_loss",
                    observable_symptoms=[
                        "coverage_notes do not mention the required schema term",
                        "initial query variants over-retrieve generic tool-use papers",
                    ],
                    recovery_hint="Audit generated query variants against required_terms before search.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-014",
            split="train",
            level=1,
            title="Synonym drift in freshness query expansion",
            user_prompt=(
                "Find papers about literature-watch freshness and temporal drift. Avoid query variants "
                "that drift into general workflow automation."
            ),
            available_tools=["synthesize_query", "search_catalog", "fetch_metadata", "filter_papers", "save_lit_report"],
            must_include=["LIT-012"],
            must_exclude=["LIT-017"],
            required_facets=["freshness_query", "drift_detection", "fault_attribution"],
            trace=[
                step(1, "synthesize_query", "generate freshness query variants", "one variant drifts into workflow automation"),
                step(2, "search_catalog", "search corrected freshness query", "candidate ids include LIT-012"),
                step(3, "filter_papers", "exclude workflow automation drift", "LIT-017 is excluded"),
                step(4, "save_lit_report", "save query drift note", "report attributes drift to synthesize_query"),
            ],
            injections=[
                inj(
                    injection_id="INJ-QUERY-DRIFT-001",
                    target_tool="synthesize_query",
                    failure_mode_id="synthesize_query.fm.synonym_drift",
                    trigger={"goal_contains": "temporal drift"},
                    injected_behavior="Add a query variant for generic workflow automation instead of temporal metadata drift.",
                    ground_truth_attribution="tool.synthesize_query.synonym_drift",
                    observable_symptoms=[
                        "query variant introduces workflow automation with no freshness term",
                        "search results include LIT-017 despite the temporal-drift goal",
                    ],
                    recovery_hint="Drop drifted variants before search or filter their results explicitly.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-015",
            split="dev",
            level=1,
            title="Forbidden term leak in screening search",
            user_prompt=(
                "Search for systematic-review screening papers while explicitly avoiding recommendation-only work."
            ),
            available_tools=["synthesize_query", "search_catalog", "filter_papers", "fetch_metadata", "save_lit_report"],
            must_include=["LIT-006", "LIT-010", "LIT-020"],
            must_exclude=["LIT-014"],
            required_facets=["forbidden_term_audit", "screening", "fault_attribution"],
            trace=[
                step(1, "synthesize_query", "generate screening queries", "injected query leaks forbidden recommendation term"),
                step(2, "search_catalog", "search after forbidden-term audit", "results emphasize screening papers"),
                step(3, "filter_papers", "exclude recommendation-only candidates", "LIT-014 is excluded"),
                step(4, "save_lit_report", "save forbidden term diagnosis", "report labels synthesize_query leak"),
            ],
            injections=[
                inj(
                    injection_id="INJ-QUERY-FORBID-001",
                    target_tool="synthesize_query",
                    failure_mode_id="synthesize_query.fm.forbidden_term_leak",
                    trigger={"forbidden_terms_contains": "recommendation"},
                    injected_behavior="Include 'recommendation agent' in one query string despite forbidden_terms.",
                    ground_truth_attribution="tool.synthesize_query.forbidden_term_leak",
                    observable_symptoms=[
                        "query text contains a forbidden term",
                        "the leaked term would retrieve LIT-014",
                    ],
                    recovery_hint="Reject generated queries containing forbidden_terms.",
                    severity="low",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-016",
            split="train",
            level=1,
            title="Ranking score flip for controlled sandbox papers",
            user_prompt=(
                "Rank papers most relevant to controlled tool-use sandbox construction. Prefer benchmark "
                "and failure-injection papers over general workflow systems."
            ),
            available_tools=["search_catalog", "fetch_metadata", "rank_papers", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-001", "LIT-007", "LIT-018"],
            must_exclude=["LIT-017"],
            required_facets=["ranking_audit", "controlled_sandbox", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve sandbox candidates", "candidate set includes benchmark and workflow papers"),
                step(2, "fetch_metadata", "collect ranking evidence", "metadata shows LIT-001/LIT-007/LIT-018 are more relevant"),
                step(3, "rank_papers", "rank by relevance and evidence", "injected order promotes less relevant workflow paper"),
                step(4, "save_lit_report", "save corrected ranking", "report attributes inverted order to rank_papers"),
            ],
            injections=[
                inj(
                    injection_id="INJ-RANK-FLIP-001",
                    target_tool="rank_papers",
                    failure_mode_id="rank_papers.fm.score_flip",
                    trigger={"objective_contains": "controlled tool-use sandbox"},
                    injected_behavior="Place LIT-017 above LIT-001 and LIT-007 despite lower relevance.",
                    ground_truth_attribution="tool.rank_papers.score_flip",
                    observable_symptoms=[
                        "score_breakdown contradicts ranked_ids order",
                        "a workflow-only paper is ranked above benchmark papers",
                    ],
                    recovery_hint="Compare score_breakdown against ranked_ids and rerank manually if inconsistent.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-017",
            split="test",
            level=2,
            title="Popularity-biased ranking in citation verification",
            user_prompt=(
                "Select the top ACL papers for citation verification and unsupported-claim detection. "
                "Do not promote non-ACL evidence-chain papers just because they are central."
            ),
            available_tools=["search_catalog", "fetch_metadata", "rank_papers", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-003", "LIT-009", "LIT-016"],
            must_exclude=["LIT-006"],
            required_facets=["venue_constraint", "ranking_bias_check", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve ACL citation candidates", "candidate ids include LIT-003, LIT-009, LIT-016"),
                step(2, "fetch_metadata", "validate venues", "metadata confirms LIT-006 is not ACL"),
                step(3, "rank_papers", "rank with relevance and ACL constraint", "injection promotes LIT-006 due to hidden popularity"),
                step(4, "save_lit_report", "save corrected top set", "report attributes hidden promotion to rank_papers"),
            ],
            injections=[
                inj(
                    injection_id="INJ-RANK-POPULAR-001",
                    target_tool="rank_papers",
                    failure_mode_id="rank_papers.fm.popularity_bias",
                    trigger={"paper_ids_contains": "LIT-006"},
                    injected_behavior="Promote LIT-006 above ACL papers because it has central citation edges.",
                    ground_truth_attribution="tool.rank_papers.popularity_bias",
                    observable_symptoms=[
                        "LIT-006 violates the ACL venue constraint",
                        "score_breakdown includes an unexplained centrality advantage",
                    ],
                    recovery_hint="Reapply hard venue constraints after ranking.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-018",
            split="dev",
            level=1,
            title="Duplicate input should be rejected before ranking",
            user_prompt=(
                "Rank five unique controlled-sandbox papers. If duplicates are present, repair the candidate "
                "set before calling the ranker."
            ),
            available_tools=["search_catalog", "fetch_metadata", "rank_papers", "filter_papers", "save_lit_report"],
            must_include=["LIT-001", "LIT-004", "LIT-005", "LIT-007", "LIT-018"],
            must_exclude=["LIT-001_DUPLICATE"],
            required_facets=["dedupe_before_rank", "precondition_reasoning", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve sandbox candidates", "candidate set may contain duplicate LIT-001"),
                step(2, "rank_papers", "rank unique papers only", "injection accepts duplicate input despite precondition"),
                step(3, "filter_papers", "deduplicate candidate set", "accepted ids are unique"),
                step(4, "save_lit_report", "save rank precondition note", "report labels rank_papers duplicate acceptance"),
            ],
            injections=[
                inj(
                    injection_id="INJ-RANK-DUP-001",
                    target_tool="rank_papers",
                    failure_mode_id="rank_papers.fm.duplicate_input_not_rejected",
                    trigger={"paper_ids_has_duplicates": True},
                    injected_behavior="Return a ranking for duplicate paper_ids instead of rejecting the call.",
                    ground_truth_attribution="tool.rank_papers.duplicate_input_not_rejected",
                    observable_symptoms=[
                        "ranker precondition says paper_ids must be unique",
                        "ranked_ids still contains repeated LIT-001",
                    ],
                    recovery_hint="Deduplicate locally and rerun ranking.",
                    severity="low",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-019",
            split="train",
            level=1,
            title="Polarity flip in negative-results extraction",
            user_prompt=(
                "Summarize negative evidence about autonomous paper recommendation agents and explain why "
                "it should not be used as positive support for review-screening agents."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "extract_claims", "save_lit_report"],
            must_include=["LIT-014"],
            must_exclude=["LIT-010"],
            required_facets=["negative_result", "claim_polarity", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "find recommendation negative-results paper", "candidate ids include LIT-014"),
                step(2, "retrieve_abstract", "retrieve negative evidence", "abstract states overfitting and missed unfamiliar work"),
                step(3, "extract_claims", "extract limitation claims", "injection flips limitation into positive capability"),
                step(4, "save_lit_report", "save corrected negative summary", "report attributes polarity flip to extract_claims"),
            ],
            injections=[
                inj(
                    injection_id="INJ-CLAIM-POLARITY-001",
                    target_tool="extract_claims",
                    failure_mode_id="extract_claims.fm.polarity_flip",
                    trigger={"paper_ids_contains": "LIT-014", "claim_types_contains": "limitation"},
                    injected_behavior="Extract 'paper recommendation agents robustly discover unfamiliar work' from a negative-results abstract.",
                    ground_truth_attribution="tool.extract_claims.polarity_flip",
                    observable_symptoms=[
                        "claim polarity contradicts the abstract",
                        "the claim converts a limitation into a positive capability",
                    ],
                    recovery_hint="Compare extracted claims against retrieved abstract polarity.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-020",
            split="test",
            level=2,
            title="Unsupported claim in survey-generation evidence",
            user_prompt=(
                "Extract claims about survey-generation citation support. Mark unsupported claims explicitly "
                "instead of citing them as facts."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "extract_claims", "save_lit_report"],
            must_include=["LIT-016", "LIT-003"],
            must_exclude=["LIT-017"],
            required_facets=["claim_support_check", "unsupported_claims", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve survey citation-support papers", "candidate ids include LIT-016 and LIT-003"),
                step(2, "retrieve_abstract", "retrieve evidence", "abstracts support claim verification but not all generated claims"),
                step(3, "extract_claims", "extract claims and unsupported list", "injection emits unsupported claim as supported"),
                step(4, "save_lit_report", "save claim-support audit", "report attributes unsupported emitted claim to extract_claims"),
            ],
            injections=[
                inj(
                    injection_id="INJ-CLAIM-UNSUPPORTED-001",
                    target_tool="extract_claims",
                    failure_mode_id="extract_claims.fm.unsupported_claim",
                    trigger={"claim_types_contains": "metric"},
                    injected_behavior="Emit a claim that CiteGuard reduces hallucinations by 90%, although no abstract states that metric.",
                    ground_truth_attribution="tool.extract_claims.unsupported_claim",
                    observable_symptoms=[
                        "metric claim has no matching abstract snippet",
                        "unsupported list omits the invented metric",
                    ],
                    recovery_hint="Require snippet-backed support for every metric claim.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-021",
            split="dev",
            level=1,
            title="Missing limitation during tool-contract synthesis",
            user_prompt=(
                "Extract method and limitation claims from tool-contract papers. Include limitations about "
                "manual contracts or heavy engineering when evidence supports them."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "extract_claims", "save_lit_report"],
            must_include=["LIT-002", "LIT-015", "LIT-019"],
            must_exclude=["LIT-014"],
            required_facets=["limitations", "tool_contracts", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve contract papers", "candidate ids include LIT-002, LIT-015, LIT-019"),
                step(2, "retrieve_abstract", "collect method evidence", "abstracts mention contracts and preconditions"),
                step(3, "extract_claims", "extract method and limitation claims", "injection omits limitation evidence"),
                step(4, "save_lit_report", "save balanced claim table", "report notes missing limitation extraction"),
            ],
            injections=[
                inj(
                    injection_id="INJ-CLAIM-MISSING-LIMIT-001",
                    target_tool="extract_claims",
                    failure_mode_id="extract_claims.fm.missing_limitation",
                    trigger={"claim_types_contains": "limitation"},
                    injected_behavior="Omit available limitation claims about manual contracts and engineering burden.",
                    ground_truth_attribution="tool.extract_claims.missing_limitation",
                    observable_symptoms=[
                        "method claims are present but limitation claims are empty",
                        "task asks explicitly for limitations",
                    ],
                    recovery_hint="Re-read abstracts for negative or caveat language.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-022",
            split="train",
            level=2,
            title="WorkflowIR validator misses missing metadata dependency",
            user_prompt=(
                "Create a WorkflowIR plan for an annotated bibliography. The plan must fetch metadata before "
                "BibTeX export and validate this dependency before execution."
            ),
            available_tools=["validate_workflow_ir", "search_catalog", "fetch_metadata", "export_bibtex", "save_lit_report"],
            must_include=["LIT-002", "LIT-015", "LIT-019"],
            must_exclude=["LIT-014"],
            required_facets=["workflow_ir", "dependency_check", "fault_attribution"],
            trace=[
                step(1, "validate_workflow_ir", "validate proposed bibliography workflow", "injection misses export before metadata dependency error"),
                step(2, "search_catalog", "retrieve contract papers", "candidate ids include bibliography targets"),
                step(3, "fetch_metadata", "repair dependency by fetching metadata", "metadata available before export"),
                step(4, "export_bibtex", "export after repair", "BibTeX uses validated metadata"),
                step(5, "save_lit_report", "save workflow validation note", "report labels validator false negative"),
            ],
            injections=[
                inj(
                    injection_id="INJ-VALIDATOR-FN-001",
                    target_tool="validate_workflow_ir",
                    failure_mode_id="validate_workflow_ir.fm.false_negative",
                    trigger={"checks_contains": "dataflow"},
                    injected_behavior="Return status=ready for a workflow where export_bibtex runs before fetch_metadata.",
                    ground_truth_attribution="tool.validate_workflow_ir.false_negative",
                    observable_symptoms=[
                        "workflow edge order violates export_bibtex preconditions",
                        "validator reports no blocking_errors",
                    ],
                    recovery_hint="Run deterministic dependency checks over tool preconditions and effects.",
                    severity="high",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-023",
            split="test",
            level=2,
            title="WorkflowIR validator false positive blocks valid search",
            user_prompt=(
                "Validate and execute a simple WorkflowIR plan: synthesize query, search catalog, fetch metadata, "
                "then save a report on query expansion papers."
            ),
            available_tools=["validate_workflow_ir", "synthesize_query", "search_catalog", "fetch_metadata", "save_lit_report"],
            must_include=["LIT-004", "LIT-008", "LIT-020"],
            must_exclude=["LIT-014"],
            required_facets=["false_positive_check", "query_expansion", "fault_attribution"],
            trace=[
                step(1, "validate_workflow_ir", "validate simple query-expansion workflow", "injection blocks a valid workflow"),
                step(2, "synthesize_query", "generate query expansion search", "query variants satisfy constraints"),
                step(3, "search_catalog", "retrieve query papers", "candidate ids include LIT-004, LIT-008, LIT-020"),
                step(4, "save_lit_report", "save validator diagnosis", "report labels validator false positive"),
            ],
            injections=[
                inj(
                    injection_id="INJ-VALIDATOR-FP-001",
                    target_tool="validate_workflow_ir",
                    failure_mode_id="validate_workflow_ir.fm.false_positive",
                    trigger={"checks_contains": "schema"},
                    injected_behavior="Return status=blocked for a workflow whose nodes and schemas are valid.",
                    ground_truth_attribution="tool.validate_workflow_ir.false_positive",
                    observable_symptoms=[
                        "blocking error cites no concrete invalid field",
                        "all workflow node tool ids are available",
                    ],
                    recovery_hint="Inspect the diagnostic details and execute after independent schema validation.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-024",
            split="train",
            level=2,
            title="WorkflowIR diagnostic points to wrong node",
            user_prompt=(
                "Diagnose a WorkflowIR plan that fails because retrieve_abstract is called before selecting a paper id. "
                "Localize the error to the minimum wrong node or edge."
            ),
            available_tools=["validate_workflow_ir", "search_catalog", "fetch_metadata", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-001", "LIT-007"],
            must_exclude=["LIT-014"],
            required_facets=["error_localization", "minimum_subgraph", "fault_attribution"],
            trace=[
                step(1, "validate_workflow_ir", "localize wrong-order plan error", "injection points to search_catalog instead of retrieve_abstract edge"),
                step(2, "search_catalog", "repair by selecting candidates first", "search produces paper ids"),
                step(3, "retrieve_abstract", "retrieve after candidate selection", "abstract call has a valid paper_id"),
                step(4, "save_lit_report", "save localization diagnosis", "report labels mislocalized validator error"),
            ],
            injections=[
                inj(
                    injection_id="INJ-VALIDATOR-MISLOC-001",
                    target_tool="validate_workflow_ir",
                    failure_mode_id="validate_workflow_ir.fm.mislocalized_error",
                    trigger={"checks_contains": "precondition"},
                    injected_behavior="Report the failing node as search_catalog although retrieve_abstract lacks a selected paper_id.",
                    ground_truth_attribution="tool.validate_workflow_ir.mislocalized_error",
                    observable_symptoms=[
                        "diagnostic node id does not match the missing paper_id precondition",
                        "the repair target should be the edge into retrieve_abstract",
                    ],
                    recovery_hint="Map each diagnostic to the violated tool precondition.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-025",
            split="test",
            level=2,
            title="Citation graph direction flip in lineage tracing",
            user_prompt=(
                "Trace which papers are references versus cited-by neighbors for query expansion. "
                "Do not confuse backward references with forward influence."
            ),
            available_tools=["search_catalog", "citation_graph", "fetch_metadata", "retrieve_abstract", "save_lit_report"],
            must_include=["LIT-004", "LIT-008", "LIT-020"],
            must_exclude=["LIT-015"],
            required_facets=["citation_direction", "lineage_trace", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "find query expansion seeds", "candidate ids include LIT-008 and LIT-020"),
                step(2, "citation_graph", "expand references and cited_by separately", "injection flips directions"),
                step(3, "fetch_metadata", "validate neighbor topics", "metadata supports query-expansion lineage"),
                step(4, "save_lit_report", "save direction-flip diagnosis", "report labels citation_graph direction flip"),
            ],
            injections=[
                inj(
                    injection_id="INJ-GRAPH-DIRECTION-001",
                    target_tool="citation_graph",
                    failure_mode_id="citation_graph.fm.direction_flip",
                    trigger={"direction": "both", "seed_ids_contains": "LIT-008"},
                    injected_behavior="Swap references and cited_by labels for edges around LIT-008.",
                    ground_truth_attribution="tool.citation_graph.direction_flip",
                    observable_symptoms=[
                        "edge direction contradicts corpus citations",
                        "forward and backward lineage explanations are reversed",
                    ],
                    recovery_hint="Compare graph edges against citation lists in corpus metadata.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-026",
            split="train",
            level=1,
            title="Missing citation edge during benchmark repair",
            user_prompt=(
                "Use citation expansion to repair benchmark search results. Identify if a missing edge hides "
                "a relevant benchmark leakage paper."
            ),
            available_tools=["search_catalog", "citation_graph", "fetch_metadata", "save_lit_report"],
            must_include=["LIT-001", "LIT-007", "LIT-018"],
            must_exclude=["LIT-014"],
            required_facets=["missing_edge_check", "benchmark_repair", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve benchmark seeds", "candidate ids include LIT-001 and LIT-007"),
                step(2, "citation_graph", "expand benchmark citations", "injection omits LIT-001 -> LIT-018"),
                step(3, "fetch_metadata", "validate recovered benchmark papers", "metadata confirms LIT-018 if recovered by alternate search"),
                step(4, "save_lit_report", "save missing-edge diagnosis", "report labels citation_graph missing edge"),
            ],
            injections=[
                inj(
                    injection_id="INJ-GRAPH-MISSING-001",
                    target_tool="citation_graph",
                    failure_mode_id="citation_graph.fm.missing_edge",
                    trigger={"seed_ids_contains": "LIT-001"},
                    injected_behavior="Omit the real edge LIT-001 -> LIT-018 from citation expansion.",
                    ground_truth_attribution="tool.citation_graph.missing_edge",
                    observable_symptoms=[
                        "corpus citations for LIT-001 include LIT-018",
                        "graph output lacks that edge",
                    ],
                    recovery_hint="Cross-check citation_graph output with fetched citation metadata or rerun search with leakage terms.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-027",
            split="dev",
            level=1,
            title="Comparison row alignment error",
            user_prompt=(
                "Compare TraceBench, ToolSandbox, and Failure Attribution by artifact, contract fields, "
                "and failure modes. Ensure rows are aligned to the right paper ids."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "compare_methods", "save_lit_report"],
            must_include=["LIT-001", "LIT-005", "LIT-007"],
            must_exclude=["LIT-014"],
            required_facets=["row_alignment", "artifact_type", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve three comparison papers", "candidate ids include LIT-001, LIT-005, LIT-007"),
                step(2, "retrieve_abstract", "collect evidence", "abstracts distinguish benchmark, sandbox, and taxonomy"),
                step(3, "compare_methods", "build aligned table", "injection shifts cells across rows"),
                step(4, "save_lit_report", "save corrected comparison", "report labels compare_methods row alignment"),
            ],
            injections=[
                inj(
                    injection_id="INJ-COMPARE-ROWS-001",
                    target_tool="compare_methods",
                    failure_mode_id="compare_methods.fm.misaligned_rows",
                    trigger={"paper_ids_contains": "LIT-005"},
                    injected_behavior="Place LIT-005 taxonomy cells into the LIT-007 row.",
                    ground_truth_attribution="tool.compare_methods.row_alignment",
                    observable_symptoms=[
                        "row content contradicts paper titles",
                        "taxonomy language appears under ToolSandbox",
                    ],
                    recovery_hint="Cross-check every row against metadata title and abstract terms.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-028",
            split="test",
            level=1,
            title="Omitted limitations in method comparison",
            user_prompt=(
                "Compare WorkflowIR-adjacent papers and include limitations or risks where evidence supports them."
            ),
            available_tools=["search_catalog", "fetch_metadata", "retrieve_abstract", "compare_methods", "extract_claims", "save_lit_report"],
            must_include=["LIT-015", "LIT-019", "LIT-017"],
            must_exclude=["LIT-014"],
            required_facets=["limitations", "method_comparison", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve WorkflowIR-adjacent papers", "candidate ids include typed effects, preconditions, workflow automation"),
                step(2, "retrieve_abstract", "collect evidence", "abstracts support methods and caveats"),
                step(3, "compare_methods", "compare including limitations", "injection drops known limitations"),
                step(4, "extract_claims", "recover limitation evidence", "claim extraction supplies omitted caveats"),
                step(5, "save_lit_report", "save limitation-aware comparison", "report attributes omission to compare_methods"),
            ],
            injections=[
                inj(
                    injection_id="INJ-COMPARE-LIMIT-001",
                    target_tool="compare_methods",
                    failure_mode_id="compare_methods.fm.missing_negative_evidence",
                    trigger={"dimensions_contains": "limitations"},
                    injected_behavior="Omit limitation cells for workflow and contract papers.",
                    ground_truth_attribution="tool.compare_methods.omitted_limitations",
                    observable_symptoms=[
                        "limitations column is empty for all rows",
                        "task explicitly requires risks/limitations",
                    ],
                    recovery_hint="Use extract_claims with limitation claim type to audit the table.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-029",
            split="train",
            level=1,
            title="Deduplication loss during bibliography export",
            user_prompt=(
                "Export distinct bibliography entries for schema drift, typed effects, and precondition checking. "
                "Deduplication should not remove distinct papers."
            ),
            available_tools=["search_catalog", "fetch_metadata", "export_bibtex", "save_lit_report"],
            must_include=["LIT-002", "LIT-015", "LIT-019"],
            must_exclude=[],
            required_facets=["distinct_entries", "bibtex_deduplication", "fault_attribution"],
            trace=[
                step(1, "search_catalog", "retrieve bibliography targets", "candidate ids include LIT-002, LIT-015, LIT-019"),
                step(2, "fetch_metadata", "collect stable metadata", "metadata confirms distinct titles and dois"),
                step(3, "export_bibtex", "export with deduplicate=true", "injection removes a distinct paper"),
                step(4, "save_lit_report", "save export-loss warning", "report labels deduplication loss"),
            ],
            injections=[
                inj(
                    injection_id="INJ-BIB-DEDUP-001",
                    target_tool="export_bibtex",
                    failure_mode_id="export_bibtex.fm.deduplication_loss",
                    trigger={"deduplicate": True, "paper_ids_contains": "LIT-019"},
                    injected_behavior="Drop LIT-019 as a duplicate of LIT-015 even though DOI and title differ.",
                    ground_truth_attribution="tool.export_bibtex.deduplication_loss",
                    observable_symptoms=[
                        "export has fewer entries than distinct metadata records",
                        "no warning explains the removed LIT-019",
                    ],
                    recovery_hint="Count distinct ids before and after BibTeX export.",
                )
            ],
        ),
        make_task(
            task_id="CLS-LIT-030",
            split="test",
            level=1,
            title="Integrated clean WorkflowIR first-layer task",
            user_prompt=(
                "Run a clean end-to-end WorkflowIR-style literature search for controlled sandbox, contract, "
                "and repair papers. Produce a compact report with candidate set, evidence-backed claims, and BibTeX."
            ),
            available_tools=workflow_tools,
            must_include=["LIT-001", "LIT-002", "LIT-005", "LIT-007", "LIT-015", "LIT-019"],
            must_exclude=["LIT-014"],
            required_facets=["workflow_ir", "claims", "bibtex", "clean_trace"],
            trace=[
                step(1, "synthesize_query", "create controlled sandbox and contract query variants", "queries cover sandbox, schema, precondition, and repair"),
                step(2, "validate_workflow_ir", "validate search workflow", "workflow has no blocking errors"),
                step(3, "search_catalog", "retrieve candidates", "candidate ids include required papers"),
                step(4, "fetch_metadata", "fetch metadata", "metadata supports filtering and export"),
                step(5, "retrieve_abstract", "retrieve abstracts", "abstracts support claim extraction"),
                step(6, "rank_papers", "rank candidates", "ranking prioritizes sandbox and contract papers"),
                step(7, "extract_claims", "extract evidence-backed claims", "claims have support snippets"),
                step(8, "export_bibtex", "export references", "BibTeX includes all cited paper ids"),
                step(9, "save_lit_report", "save final report", "report contains all requested sections"),
            ],
        ),
    ]


def task_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": "https://aris.local/schemas/controlled_sandbox_litsearch_task_v1.json",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "dataset_id",
            "dataset_version",
            "task_id",
            "split",
            "level",
            "title",
            "category",
            "user_prompt",
            "available_tools",
            "initial_state",
            "success_criteria",
            "oracle",
            "expected_trace",
            "injections",
        ],
        "properties": {
            "dataset_id": {"const": DATASET_ID},
            "dataset_version": {"type": "string"},
            "task_id": {"type": "string"},
            "split": {"enum": ["train", "dev", "test"]},
            "level": {"type": "integer", "minimum": 1, "maximum": 3},
            "title": {"type": "string"},
            "category": {"type": "string"},
            "user_prompt": {"type": "string"},
            "available_tools": {"type": "array", "items": {"type": "string"}},
            "initial_state": {"type": "object"},
            "success_criteria": {"type": "array", "items": {"type": "string"}},
            "oracle": {
                "type": "object",
                "required": [
                    "must_include_paper_ids",
                    "must_exclude_paper_ids",
                    "required_answer_facets",
                    "ground_truth_attribution_labels",
                ],
            },
            "expected_trace": {"type": "array", "items": {"type": "object"}},
            "injections": {"type": "array", "items": {"type": "object"}},
        },
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=False) + "\n", encoding="utf-8")


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, sort_keys=False) + "\n")


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as handle:
        return [json.loads(line) for line in handle if line.strip()]


def validate_dataset(out_dir: Path) -> list[str]:
    errors: list[str] = []
    tools = read_json(out_dir / "tools.json")
    rows = read_jsonl(out_dir / "tasks.jsonl")
    papers = read_jsonl(out_dir / "corpus.jsonl")
    taxonomy = read_json(out_dir / "attribution_taxonomy.json")
    splits = read_json(out_dir / "splits.json")

    tool_ids = {tool["tool_id"] for tool in tools}
    paper_ids = {paper["paper_id"] for paper in papers}
    labels = set(taxonomy["labels"])
    failure_modes = {
        mode["failure_mode_id"]: mode["attribution_label"]
        for tool in tools
        for mode in tool["failure_modes"]
    }

    for tool in tools:
        for required in ["input_schema", "output_schema", "preconditions", "effects", "failure_modes"]:
            if not tool.get(required):
                errors.append(f"{tool['tool_id']} missing {required}")
    if not 10 <= len(tools) <= 20:
        errors.append(f"HTML first-layer target requires 10-20 tools; found {len(tools)}")

    seen_tasks: set[str] = set()
    split_members = {"train": [], "dev": [], "test": []}
    for row in rows:
        task_id = row["task_id"]
        if task_id in seen_tasks:
            errors.append(f"duplicate task id {task_id}")
        seen_tasks.add(task_id)
        split_members[row["split"]].append(task_id)

        unknown_tools = set(row["available_tools"]) - tool_ids
        if unknown_tools:
            errors.append(f"{task_id} references unknown tools: {sorted(unknown_tools)}")
        for trace_step in row["expected_trace"]:
            if trace_step["tool_id"] not in tool_ids:
                errors.append(f"{task_id} trace references unknown tool {trace_step['tool_id']}")

        for paper_id in row["oracle"]["must_include_paper_ids"]:
            if paper_id not in paper_ids:
                errors.append(f"{task_id} must_include unknown paper id {paper_id}")
        for paper_id in row["oracle"]["must_exclude_paper_ids"]:
            if paper_id.startswith("LIT-") and paper_id != "LIT-999" and paper_id != "LIT-001_DUPLICATE" and paper_id not in paper_ids:
                errors.append(f"{task_id} must_exclude unknown paper id {paper_id}")

        for label in row["oracle"]["ground_truth_attribution_labels"]:
            if label not in labels:
                errors.append(f"{task_id} unknown attribution label {label}")

        for injection in row["injections"]:
            target_tool = injection["target_tool"]
            failure_mode_id = injection["failure_mode_id"]
            if target_tool not in tool_ids:
                errors.append(f"{task_id} injection targets unknown tool {target_tool}")
            if failure_mode_id not in failure_modes:
                errors.append(f"{task_id} injection references unknown failure mode {failure_mode_id}")
            expected_label = failure_modes.get(failure_mode_id)
            actual_label = injection["ground_truth_attribution"]
            if expected_label != actual_label:
                errors.append(
                    f"{task_id} injection {injection['injection_id']} attribution {actual_label} "
                    f"does not match tool failure mode label {expected_label}"
                )

    if splits != split_members:
        errors.append("splits.json does not match task split membership")
    if not 30 <= len(rows) <= 50:
        errors.append(f"HTML first-layer target requires 30-50 tasks; found {len(rows)}")
    return errors


def build_manifest(out_dir: Path, tools: list[dict[str, Any]], papers: list[dict[str, Any]], rows: list[dict[str, Any]]) -> dict[str, Any]:
    split_counts: dict[str, int] = {"train": 0, "dev": 0, "test": 0}
    injected = 0
    tool_coverage: Counter[str] = Counter()
    attribution_coverage: Counter[str] = Counter()
    for row in rows:
        split_counts[row["split"]] += 1
        if row["injections"]:
            injected += 1
        for tool_id in row["available_tools"]:
            tool_coverage[tool_id] += 1
        for label in row["oracle"]["ground_truth_attribution_labels"]:
            attribution_coverage[label] += 1
    return {
        "dataset_id": DATASET_ID,
        "dataset_version": DATASET_VERSION,
        "dataset_date": DATASET_DATE,
        "description": "Controlled offline literature-search sandbox for multi-tool research agents.",
        "out_dir": str(out_dir),
        "files": {
            "tools": "tools.json",
            "corpus": "corpus.jsonl",
            "tasks": "tasks.jsonl",
            "task_schema": "task_schema.json",
            "attribution_taxonomy": "attribution_taxonomy.json",
            "splits": "splits.json",
            "evaluation_rubric": "evaluation_rubric.json",
            "readme": "README.md",
        },
        "counts": {
            "tools": len(tools),
            "papers": len(papers),
            "tasks": len(rows),
            "tasks_with_injection": injected,
            "tasks_clean": len(rows) - injected,
            "splits": split_counts,
        },
        "html_first_layer_requirements": {
            "planned_layer": "Controlled Sandbox",
            "target_tasks": "30-50",
            "target_tools": "10-20",
            "tool_contract_fields": ["schema", "precondition", "effect", "failure_mode"],
            "metrics": [
                "invalid_call_rate",
                "repair_success",
                "error_localization_accuracy",
                "cost_reduction",
            ],
            "status": "complete" if 30 <= len(rows) <= 50 and 10 <= len(tools) <= 20 else "incomplete",
        },
        "coverage": {
            "tool_task_counts": dict(sorted(tool_coverage.items())),
            "attribution_label_counts": dict(sorted(attribution_coverage.items())),
        },
        "design_invariants": [
            "each tool declares input_schema, output_schema, preconditions, effects, and failure_modes",
            "each injected task has a single primary ground-truth attribution label",
            "all oracle paper ids refer to the synthetic corpus unless intentionally invalid for precondition repair",
            "tool observations are meant to be enough for recovery without internet access",
        ],
    }


def evaluation_rubric() -> dict[str, Any]:
    return {
        "rubric_id": "controlled_sandbox_litsearch_eval_v1",
        "metrics": [
            {
                "metric": "success_rate",
                "definition": "Fraction of tasks whose final report satisfies must_include, must_exclude, and required_answer_facets.",
                "computed_from": ["oracle.must_include_paper_ids", "oracle.must_exclude_paper_ids", "oracle.required_answer_facets"],
            },
            {
                "metric": "invalid_call_rate",
                "definition": "Invalid tool calls divided by total tool calls, where invalid means schema, precondition, wrong-order, or unavailable-tool violation.",
                "computed_from": ["tool trace", "tools.json preconditions", "tools.json input_schema"],
            },
            {
                "metric": "repair_success",
                "definition": "Fraction of injected-fault tasks where the agent notices the symptom and recovers the oracle-required papers or report sections.",
                "computed_from": ["tasks.jsonl injections", "oracle", "final report"],
            },
            {
                "metric": "error_localization_accuracy",
                "definition": "Whether the agent's primary attribution label matches oracle.ground_truth_attribution_labels.",
                "computed_from": ["oracle.ground_truth_attribution_labels", "agent attribution output"],
            },
            {
                "metric": "cost_reduction",
                "definition": "Relative reduction in tool calls or estimated token/tool cost against a baseline trace for the same task.",
                "computed_from": ["expected_trace", "agent trace", "optional cost model"],
            },
        ],
        "baseline_families": ["ReAct", "DAG-only", "WorkflowIR without checks", "WorkflowIR full"],
    }


def readme_text(manifest: dict[str, Any]) -> str:
    return f"""# Controlled Sandbox Literature Search v1

Dataset id: `{DATASET_ID}`

This is the first-layer controlled sandbox for literature-search agents. It is
offline and synthetic by design: every paper, tool result, and injected fault can
be traced to an oracle record.

## Files

- `tools.json`: tool contracts. Every tool has schema, preconditions, effects,
  and failure modes.
- `corpus.jsonl`: synthetic scholarly corpus used by the sandbox.
- `tasks.jsonl`: task instances with prompts, allowed tools, expected traces,
  injections, and oracle labels.
- `attribution_taxonomy.json`: root-cause taxonomy and labels.
- `task_schema.json`: JSON Schema for task rows.
- `splits.json`: train/dev/test task ids.
- `evaluation_rubric.json`: first-layer metrics and baseline families.
- `manifest.json`: counts and design invariants.

## Current Scope

- Tools: {manifest["counts"]["tools"]}
- Synthetic papers: {manifest["counts"]["papers"]}
- Tasks: {manifest["counts"]["tasks"]}
- Injected tasks: {manifest["counts"]["tasks_with_injection"]}
- Clean tasks: {manifest["counts"]["tasks_clean"]}
- HTML first-layer status: {manifest["html_first_layer_requirements"]["status"]}

## Intended Evaluation

An agent should solve each `user_prompt` using only the declared tools and tool
observations. The evaluator can then score:

1. task success against `oracle.must_include_paper_ids` and
   `oracle.must_exclude_paper_ids`;
2. answer completeness against `oracle.required_answer_facets`;
3. fault attribution against `oracle.ground_truth_attribution_labels`;
4. recovery behavior against `injections[*].observable_symptoms` and
   `injections[*].recovery_hint`.

The first-layer HTML plan asks for 30-50 tasks and 10-20 tools. This generated
snapshot satisfies that target and keeps every task offline/reproducible.

## Rebuild Or Validate

```bash
python3 scripts/workflowir/build_controlled_litsearch_sandbox.py
python3 scripts/workflowir/build_controlled_litsearch_sandbox.py --validate-only
```
"""


def build_dataset(out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    tools = tool_specs()
    papers = corpus()
    rows = tasks()
    splits = {"train": [], "dev": [], "test": []}
    for row in rows:
        splits[row["split"]].append(row["task_id"])

    manifest = build_manifest(out_dir, tools, papers, rows)
    write_json(out_dir / "tools.json", tools)
    write_jsonl(out_dir / "corpus.jsonl", papers)
    write_jsonl(out_dir / "tasks.jsonl", rows)
    write_json(out_dir / "task_schema.json", task_schema())
    write_json(out_dir / "attribution_taxonomy.json", attribution_taxonomy())
    write_json(out_dir / "splits.json", splits)
    write_json(out_dir / "evaluation_rubric.json", evaluation_rubric())
    write_json(out_dir / "manifest.json", manifest)
    (out_dir / "README.md").write_text(readme_text(manifest), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=DEFAULT_OUT_DIR, help="Output dataset directory.")
    parser.add_argument("--validate-only", action="store_true", help="Validate an existing dataset directory.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = Path(args.out_dir)
    if not args.validate_only:
        build_dataset(out_dir)
    errors = validate_dataset(out_dir)
    if errors:
        raise SystemExit("Dataset validation failed:\n" + "\n".join(f"- {error}" for error in errors))
    print(f"Validated {DATASET_ID} at {out_dir}")


if __name__ == "__main__":
    main()
