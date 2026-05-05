---
type: experiment
node_id: exp:openalex-004
title: "OpenAlex Search — Industrial RLHF, PLC, SCADA, CNC Feedback Gap"
run_id: "20260427T161817Z-industrial-rlhf-plc-scada-feedback"
date: 2026-04-27T16:18:17Z
skill: openalex-search
status: completed
verdict: gap_confirmed
freshness_window: "2025-04-27 to 2026-04-27"
---

# OpenAlex Search — Industrial RLHF, PLC, SCADA, CNC Feedback Gap

**Run ID**: `20260427T161817Z-industrial-rlhf-plc-scada-feedback`
**Status**: Completed
**Verdict**: Gap confirmed

## Purpose

This run tested whether feedback-driven or self-improving industrial LLMs are already a mature subfield, especially at the low-level factory-control layer: RLHF/RLAIF, preference learning, operator feedback, PLC programming, SCADA/process control, CNC/machining, and industrial automation.

## Query Plan Summary

All query families used the 2025-04-27 to 2026-04-27 freshness window, `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS used `search` and valid OpenAlex filters only; it did not use the deprecated `title_and_abstract.search` filter.

| Query Family | Reported | Downloaded | Notes |
|---|---:|---:|---|
| `rlhf_rlaif_operator_feedback_manufacturing` | 55 | 55 | Explicit RLHF/RLAIF/preference/reward feedback in industrial context |
| `plc_llm_hitl_validation` | 75 | 75 | PLC, IEC 61131-3, ladder logic, HITL/code validation |
| `scada_llm_process_control` | 165 | 165 | SCADA, DCS, ICS, process monitoring/control |
| `cnc_robotics_llm_adaptive_control` | 23 | 23 | CNC/machining/additive manufacturing with process-quality/control terms |
| `industrial_feedback_evaluation_protocols` | 74 | 74 | Feedback + industrial + evaluation/safety/reliability terms |

**Total downloaded rows**: 392
**Total deduplicated works**: 383

## Tightening Notes

- `cnc_robotics_llm_adaptive_control` was narrowed from 15,999 initial reported works to 23 by requiring CNC/machining/process-quality terms and excluding non-industrial robot domains.
- `industrial_feedback_evaluation_protocols` was narrowed from 14,107 initial reported works to 74 by requiring a three-way intersection of feedback terms, industrial terms, and evaluation/safety terms.
- All five final query families were below 200 reported works, so no export cap was needed.

## Key Findings

1. Explicit RLHF/RLAIF/preference-learning for industrial LLMs is genuinely scarce.
2. The clearest high-value evidence is `Training LLMs for Generating IEC 61131-3 Structured Text with Online Feedback`, which uses compiler feedback and an LLM expert to improve PLC Structured Text generation.
3. LLMs currently appear more often as analysts of SCADA data, maintenance logs, and process-monitoring data than as validated controllers of industrial actions.
4. HITL/operator feedback appears across several forms: compiler feedback, expert semantic review, EEG/trust feedback, confidence-threshold intervention, and human demonstration.
5. Standardized evaluation for feedback-driven industrial LLMs is still missing; formal verification and industrial code compilation are promising anchors.

## Representative Papers

| Topic | Representative Paper |
|---|---|
| PLC feedback learning | `Training LLMs for Generating IEC 61131-3 Structured Text with Online Feedback` |
| RLHF for HRC assembly | `A reinforcement learning from human feedback based method for task allocation of human robot collaboration assembly considering human preference` |
| ICS security | `Synthesizing Inline Security Monitors for ICS Using Generative AI and FormalBench` |
| SCADA analytics | `LLMs in Wind Turbine Gearbox Failure Prediction` |
| Industrial control interpretation | `Towards Robust Industrial Control Interpretation Through Comparative Analysis of Vision-Language Models` |

## Gap Updates

- Confirms G1 and narrows it toward explicit operator-feedback/domain-adaptation loops.
- Adds G6: explicit RLHF/RLAIF/operator-feedback industrial LLMs are scarce at PLC/SCADA/CNC/control-loop level.
- Adds G7: evaluation protocols for feedback-driven industrial LLMs are not standardized.
- Adds G8: LLM-as-controller is underdeveloped compared with LLM-as-analyst.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260427T161817Z-industrial-rlhf-plc-scada-feedback/openalex/manifest.json` | Full run metadata and API params |
| `lit-watch/runs/20260427T161817Z-industrial-rlhf-plc-scada-feedback/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260427T161817Z-industrial-rlhf-plc-scada-feedback/openalex/all_results_deduped.csv` | 383 deduplicated works |
| `lit-watch/runs/20260427T161817Z-industrial-rlhf-plc-scada-feedback/openalex/all_results_deduped.jsonl` | Deduplicated raw records |
| `lit-watch/runs/20260427T161817Z-industrial-rlhf-plc-scada-feedback/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260427T161817Z-industrial-rlhf-plc-scada-feedback/SUMMARY.md` | Run summary and implications |

## Connections

[AUTO-GENERATED from graph/edges.jsonl — do not edit manually]
