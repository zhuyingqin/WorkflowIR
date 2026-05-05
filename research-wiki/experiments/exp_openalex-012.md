---
type: experiment
node_id: exp:openalex-012
title: "OpenAlex Search - Industrial LLM HITL Governance, Approval, and Audit"
run_id: "20260427T222217Z-industrial-llm-hitl-governance-approval-audit"
date: 2026-04-28T00:42:19Z
skill: openalex-search
status: completed_export_with_summary_blocker
verdict: governance_recognized_but_not_operationalized
freshness_window: "2024-04-27 to 2026-04-27"
---

# OpenAlex Search - Industrial LLM HITL Governance, Approval, and Audit

**Run ID**: `20260427T222217Z-industrial-llm-hitl-governance-approval-audit`
**Status**: OpenAlex export completed; ARIS summary stage blocked by context overflow; Codex wrote recovery summary.
**Verdict**: Industrial LLM governance is recognized but not operationalized. The literature discusses human oversight, trust, cognitive load, XAI, and human-AI teaming, but does not yet provide a deployable approval/audit/rollback/change-management stack for self-improving or workflow-agent industrial LLMs.

## Purpose

This run tested whether the literature contains concrete governance mechanisms that would make self-improving industrial LLMs, industrial copilots, and workflow agents safe enough for deployment. It focused on human-in-the-loop governance, operator feedback, approval, audit, traceability, change management, technician workflows, and work-order approval.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-27 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `industrial_llm_hitl_operator_feedback` | 17 | 17 | 1 |
| `manufacturing_llm_operator_trust_human_factors` | 153 | 153 | 1 |
| `industrial_llm_approval_audit_traceability` | 29 | 29 | 1 |
| `maintenance_llm_technician_feedback_approval` | 6 | 6 | 1 |
| `workflow_agent_human_approval_work_order` | 134 | 134 | 1 |

**Total downloaded rows**: 339
**Total deduplicated works**: 305

## Blocker Note

ARIS completed dry-run and full export, but failed before writing `SUMMARY.md` after reading the complete deduplicated CSV into context. The blocker is recorded in `BLOCKED.md`. Codex recovered by inspecting exported metadata and writing a compact `SUMMARY.md`.

## Quality Notes

The corpus is useful for governance framing but noisy for deployment evidence. Many results are generic AI governance, healthcare, finance, education, construction, software-engineering, or broad human-centered AI papers. The most relevant industrial cluster is around Industry 5.0, assembly assistants, predictive maintenance, QMS cognitive assistants, and human-robot collaboration.

## Key Findings

1. Human oversight is treated as mandatory for industrial LLMs, but usually as an assumption rather than an implemented governance protocol.
2. The strongest concrete industrial evidence remains worker-facing or maintenance-facing decision support: assembly digital intelligent assistants and human-centric predictive maintenance.
3. Approval, audit, traceability, rollback, and change-management mechanisms are under-specified for MES/ERP/CMMS/work-order execution.
4. No paper demonstrates governance for autonomous self-improvement of an industrial LLM, including safe update approval, audit trail, rollback, or recertification.
5. Evaluation metrics remain incomplete: papers discuss trust, cognitive load, accuracy, false positives, downtime, and adoption, but rarely measure approval latency, audit completeness, operator override rate, rollback success, or post-update reliability.

## Representative Papers

| Mechanism | Representative Paper |
|---|---|
| Human-AI governance and sensemaking | `Beyond human-in-the-loop: Sensemaking between artificial intelligence and human intelligence collaboration` |
| Assembly assistant | `Assessment of a large language model based digital intelligent assistant in assembly manufacturing` |
| Human-centric predictive maintenance | `Agentic AI in Smart Manufacturing: Enabling Human-Centric Predictive Maintenance Ecosystems` |
| Industry 5.0 trust | `Trust by Design: An Ethical Framework for Collaborative Intelligence Systems in Industry 5.0` |
| Industry 5.0 human-AI knowledge graph | `Managing human-AI collaborations within Industry 5.0 scenarios via knowledge graphs` |
| QMS cognitive assistant | `Large Language Model-Based Cognitive Assistants for Quality Management Systems in Manufacturing: A Requirement Analysis` |
| Maintenance agents | `Toward Autonomous LLM-Based AI Agents for Predictive Maintenance` |
| Human/humanoid loop | `Human and Humanoid-in-the-Loop Ecosystem: An Industry 5.0 Perspective` |
| Digital-twin human-AI teaming | `Enabling interoperable human-AI teaming for automation in construction and manufacturing via Digital Twins and Sliding Work Sharing ontologies` |

## Gap Updates

- Strengthens G7: industrial LLM evaluation lacks approval/audit/rollback/change-management metrics.
- Strengthens G8: LLMs remain decision-support systems because governance for safe action is not operationalized.
- Strengthens G13: self-improving industrial LLMs still lack safe update approval, audit trails, rollback, and recertification.
- Strengthens G15: work-order/MES/CMMS approval loops remain absent.
- Adds G16: industrial LLM governance for operator approval, auditability, traceability, rollback, and change management is under-specified.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260427T222217Z-industrial-llm-hitl-governance-approval-audit/openalex/manifest.json` | Full export metadata |
| `lit-watch/runs/20260427T222217Z-industrial-llm-hitl-governance-approval-audit/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260427T222217Z-industrial-llm-hitl-governance-approval-audit/openalex/all_results_deduped.csv` | 305 deduplicated works plus header |
| `lit-watch/runs/20260427T222217Z-industrial-llm-hitl-governance-approval-audit/openalex/all_results_deduped.jsonl` | 305 deduplicated raw records |
| `lit-watch/runs/20260427T222217Z-industrial-llm-hitl-governance-approval-audit/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260427T222217Z-industrial-llm-hitl-governance-approval-audit/SUMMARY.md` | Codex recovery summary |
| `lit-watch/runs/20260427T222217Z-industrial-llm-hitl-governance-approval-audit/BLOCKED.md` | ARIS summary-stage context overflow blocker |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
