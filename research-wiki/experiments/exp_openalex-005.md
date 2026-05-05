---
type: experiment
node_id: exp:openalex-005
title: "OpenAlex Search — LLM Digital Twin Process Control Feedback"
run_id: "20260427T164456Z-llm-digital-twin-process-control-feedback"
date: 2026-04-27T16:52:42Z
skill: openalex-search
status: completed
verdict: bridge_candidate_gap_confirmed
freshness_window: "2025-04-27 to 2026-04-27"
---

# OpenAlex Search — LLM Digital Twin Process Control Feedback

**Run ID**: `20260427T164456Z-llm-digital-twin-process-control-feedback`
**Status**: Completed
**Verdict**: Digital twins are a promising bridge, but closed-loop LLM control remains immature

## Purpose

This run tested whether LLM-enabled digital twins and cognitive digital twins form the missing bridge between current industrial LLM-as-analyst systems and future safe LLM-as-controller systems. The reviewer direction focused on industrial process control, closed-loop decision support, simulation-to-operation feedback, human/operator-in-the-loop validation, safety, and reliability.

## Query Plan Summary

All query families used the 2025-04-27 to 2026-04-27 freshness window, `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS used the `openalex-search` workflow with top-level `search` expressions and valid OpenAlex filters. The invalid `title_and_abstract.search` filter was explicitly avoided.

| Query Family | Reported | Downloaded | Notes |
|---|---:|---:|---|
| `llm_digital_twin_process_control` | 309 | 200 | Tightened and capped; clean core with some logistics/energy noise |
| `cognitive_digital_twin_feedback_hitl` | 51 | 51 | High precision for cognitive twins, HITL, feedback, and adaptive operation |
| `digital_twin_llm_closed_loop_safety` | 330 | 200 | Tightened and capped; useful safety/verification signal with some tangential DT safety papers |
| `scada_process_twin_llm_control` | 25 | 25 | Small SCADA/process-control set with mixed precision |
| `factory_simulation_llm_feedback` | 24 | 24 | Low-volume simulation-to-operation feedback set |

**Total downloaded rows**: 500
**Total deduplicated works**: 347

## Tightening Notes

- Two broad families remained above 300 reported works after tightening and were capped at 200 downloaded works each for the full export.
- The highest-precision family was `cognitive_digital_twin_feedback_hitl`, which directly supports the survey thread on self-aware manufacturing and operator/simulation feedback.
- The run confirmed that digital-twin terminology catches a different slice of the field than earlier RLHF/PLC/SCADA/CNC searches.

## Key Findings

1. Digital twins are an active and credible bridge from LLM reasoning toward operational industrial decision support.
2. LLM-enabled cognitive digital twins are appearing in manufacturing, reconfigurable production, capability matching, facility layout, predictive maintenance, and robot/task adaptation.
3. LLM-as-controller remains nascent. The literature more often uses LLMs for reasoning, construction, explanation, retrieval, or decision support than for validated closed-loop actuation.
4. Human-in-the-loop and operator feedback are recognized but rarely operationalized as repeatable self-improvement protocols.
5. Safety and verification are emerging through digital-twin pre-deployment validation and formal-logic ideas, but there is still no mature benchmark for industrial LLM control safety.

## Representative Papers

| Topic | Representative Paper |
|---|---|
| Cognitive manufacturing agents | `Large language model-enabled cognitive agent for self-aware manufacturing` |
| Cognitive digital twin survey | `A survey of cognitive digital twin and the potential use of LLMs` |
| Reconfigurable manufacturing | `Cognitive digital twins for capability matching toward reconfigurable manufacturing: Leveraging asset administration shells and large language models` |
| Digital-twin construction | `An LLM-guided SD-LDM Digital Twin Construction Strategy (LSDT) for multi-industrial scenarios` |
| Control verification | `LLM-Based Adaptive Control Code Generation Framework with Digital Twin-Integrated Verification for Heterogeneous Robot Systems` |
| Agentic DT decision support | `Integrating agentic AI and digital twins for intelligent decision-making systems` |

## Gap Updates

- Strengthens G4: LLM-driven digital twins are active and should be treated as a major survey cluster, not a minor application.
- Strengthens G8: even in digital-twin work, LLM-as-controller is still much less mature than LLM-as-analyst or LLM-as-decision-support.
- Adds G9: digital-twin-mediated safety validation and simulation-to-operation feedback for industrial LLM control lack standardized closed-loop benchmarks and operator-feedback protocols.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260427T164456Z-llm-digital-twin-process-control-feedback/openalex/manifest.json` | Full run metadata and API params |
| `lit-watch/runs/20260427T164456Z-llm-digital-twin-process-control-feedback/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260427T164456Z-llm-digital-twin-process-control-feedback/openalex/all_results_deduped.csv` | 347 deduplicated works |
| `lit-watch/runs/20260427T164456Z-llm-digital-twin-process-control-feedback/openalex/all_results_deduped.jsonl` | Deduplicated raw records |
| `lit-watch/runs/20260427T164456Z-llm-digital-twin-process-control-feedback/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260427T164456Z-llm-digital-twin-process-control-feedback/SUMMARY.md` | Run summary and implications |

## Connections

[AUTO-GENERATED from graph/edges.jsonl — do not edit manually]
