---
type: experiment
node_id: exp:openalex-013
title: "OpenAlex Search - Industrial LLM Functional Safety Assurance"
run_id: "20260428T010226Z-industrial-llm-functional-safety-assurance"
date: 2026-04-28T01:06:58Z
skill: openalex-search
status: completed
verdict: functional_safety_blocks_autonomous_industrial_llm_agents
freshness_window: "2024-04-27 to 2026-04-28"
---

# OpenAlex Search - Industrial LLM Functional Safety Assurance

**Run ID**: `20260428T010226Z-industrial-llm-functional-safety-assurance`
**Status**: Completed
**Verdict**: Functional safety remains a fundamental blocker for autonomous industrial LLM agents. Limited but genuine pathways exist for LLM copilots as human-in-the-loop safety risk-analysis aids, especially around ISO 12100 and ISO 13849.

## Purpose

This run tested whether industrial LLM literature has credible pathways from copilots or workflow agents to safety-certified deployment. It focused on functional safety, safety assurance, safety cases, certification, runtime monitoring, fail-safe design, PLC/SCADA safety verification, and V&V for industrial LLM systems.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-28 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran dry-runs first and tightened broad families before export.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `industrial_llm_functional_safety_assurance` | 7 | 7 | 1 |
| `llm_safety_case_industrial_agents` | 18 | 18 | 1 |
| `llm_industrial_safety_standards` | 4 | 4 | 1 |
| `llm_runtime_monitoring_fail_safe_manufacturing` | 43 | 43 | 1 |
| `llm_control_system_safety_verification` | 42 | 42 | 1 |

**Total downloaded rows**: 114
**Total deduplicated works**: 105

## Query Tightening Notes

- `llm_safety_case_industrial_agents` initially returned 1285 works because `verification validation` matched generic LLM evaluation noise. It was tightened to explicit `"safety case"` plus industrial/manufacturing context, returning 18 works.
- `generative_ai_industrial_safety_standards` initially returned 463 works. It was reframed as `llm_industrial_safety_standards` with explicit IEC/ISO standard terms, returning 4 works.
- The small standards-family count is informative: few papers explicitly connect LLMs to IEC 61508, IEC 62443, ISO 13849, or ISO 12100.

## Key Findings

1. Only two papers genuinely address industrial machinery functional-safety risk assessment with LLMs: one ISO 13849/ISO 12100 structured prompting paper and one ISO 12100 HITL ChatGPT risk-analysis paper.
2. No paper proposes or demonstrates an LLM as a SIL-rated or safety-certified industrial control element.
3. No formal verification of LLM behavior in safety-critical industrial loops was found.
4. No runtime monitoring architecture with verified fail-safe fallback for industrial LLM agents was found.
5. IEC 62443-adjacent OT cybersecurity evidence exists, especially PLC code security, but this is not equivalent to IEC 61508/ISO 13849 functional safety.
6. HITL expert review is the only credible near-term safety pattern; LLMs can assist safety analysis, but humans remain compliance gates.

## Representative Papers

| Mechanism | Representative Paper |
|---|---|
| ISO 13849 PL classification | `Evaluation of Automated Machinery Functional Safety Risk Assessment Using LLMs` |
| ISO 12100 HITL risk analysis | `Clever Hans in the Loop? A Critical Examination of ChatGPT in a Human-in-the-Loop Framework for Machinery Functional Safety Risk Analysis` |
| Standards-aligned LLM failure taxonomy | `Beyond Next-Token Prediction: A Standards-Aligned Survey of Autoregressive LLM Failure Modes` |
| ML safety assurance | `Safety assurance of Machine Learning for autonomous systems` |
| Industry 5.0 trust framework | `Trust by Design: An Ethical Framework for Collaborative Intelligence Systems in Industry 5.0` |
| Industrial plant LLM interface | `Multimodal Cognitive Architecture with Local Generative AI for Industrial Control of Concrete Plants` |
| Oilfield ICS anomaly detection | `An Anomaly Detection Method for Oilfield Industrial Control Systems Fine-Tuned Using LLM` |
| PLC code security | `Fine-Tune LLMs for PLC Code Security: An Information-Theoretic Analysis` |

## Gap Updates

- Strengthens G7: industrial LLM evaluation lacks functional-safety V&V, safety-case, runtime-monitoring, and fail-safe metrics.
- Strengthens G8: no autonomous safety-certified controller or remediator based on LLMs was found.
- Strengthens G10: no cross-domain benchmark exists for IEC/ISO-compliant industrial LLM safety assurance.
- Strengthens G11: no production-grade, safety-certified edge/on-prem industrial LLM or SLM controller exists.
- Strengthens G13: self-improving industrial LLMs would require recertification and safety-case updates that are not addressed.
- Strengthens G16: governance remains incomplete without safety cases, formal assurance, runtime monitors, and fail-safe fallback.
- Adds G17: safety-certified autonomous industrial LLM agents lack functional-safety assurance cases, formal verification, runtime monitoring, fail-safe fallback, and IEC 61508/ISO 13849 certification pathways.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260428T010226Z-industrial-llm-functional-safety-assurance/openalex/manifest.json` | Full export metadata |
| `lit-watch/runs/20260428T010226Z-industrial-llm-functional-safety-assurance/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260428T010226Z-industrial-llm-functional-safety-assurance/openalex/all_results_deduped.csv` | 105 deduplicated works plus header |
| `lit-watch/runs/20260428T010226Z-industrial-llm-functional-safety-assurance/openalex/all_results_deduped.jsonl` | 105 deduplicated raw records |
| `lit-watch/runs/20260428T010226Z-industrial-llm-functional-safety-assurance/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260428T010226Z-industrial-llm-functional-safety-assurance/SUMMARY.md` | Run summary and safety implications |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
