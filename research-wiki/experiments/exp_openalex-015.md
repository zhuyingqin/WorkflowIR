---
type: experiment
node_id: exp:openalex-015
title: "OpenAlex Search - Industrial LLM Operator Human-Factors Evidence"
run_id: "20260428T015556Z-industrial-llm-operator-human-factors"
date: 2026-04-28T02:04:00Z
skill: openalex-search
status: completed
verdict: industrial_llm_hitl_human_factors_not_validated
freshness_window: "2024-04-27 to 2026-04-28"
---

# OpenAlex Search - Industrial LLM Operator Human-Factors Evidence

**Run ID**: `20260428T015556Z-industrial-llm-operator-human-factors`
**Status**: Completed
**Verdict**: HITL is still mostly an assumed safety and governance pattern for industrial LLMs, not an empirically validated operational mechanism. The literature contains a small number of useful operator-facing studies, but standard human-factors measures such as NASA-TLX, SUS, approval latency, and override rate are largely absent.

## Purpose

This run tested whether industrial LLM and GenAI systems have empirical evidence about the human operator: trust, cognitive load, usability, acceptance, reliance/overreliance, handoff, override behavior, approval burden, maintenance technician decision support, and HITL safety behavior.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-28 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran dry-runs first, replaced an empty handoff/override family, then exported all final queries.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `llm_assembly_operator_cognitive_load` | 145 | 145 | 1 |
| `industrial_llm_operator_trust_overreliance` | 51 | 51 | 1 |
| `genai_manufacturing_worker_usability_acceptance` | 113 | 113 | 1 |
| `llm_maintenance_technician_decision_support` | 188 | 188 | 1 |
| `llm_approval_override_operator_behavior` | 64 | 64 | 1 |

**Total downloaded rows**: 561
**Total deduplicated works**: 516

## Query Tightening Notes

- The initial `industrial_copilot_override_handoff_human_factors` query returned 0 works because it required the exact phrase `industrial copilot` plus LLM and override/handoff terms.
- It was relaxed to `llm_approval_override_operator_behavior`, returning 64 works.
- All final query families remained below the 300-work threshold.

## Key Findings

1. The 516-work corpus is dominated by conceptual/framework papers, reviews, and adoption surveys rather than empirical operator studies.
2. ARIS estimated only about 35-40 papers, roughly 7%, contain any empirical human-subject signal with industrial operators.
3. Field or industrial human-subject evidence is sparse, with the strongest recurring paper being `Assessment of a large language model based digital intelligent assistant in assembly manufacturing`.
4. Standard human-factors instruments are almost absent: no explicit NASA-TLX study, no explicit System Usability Scale study, no measured approval latency, and no measured override/approval rate in the retrieved industrial LLM set.
5. Trust, explainability, safety, and HITL are frequently mentioned, but mostly as design principles, not as measured outcomes.
6. No paper validates HITL as a safety mechanism by measuring whether human oversight prevents unsafe LLM actions or improves safety outcomes over time.

## Representative Papers

| Evidence Type | Representative Paper | Takeaway |
|---|---|---|
| Field/industrial human-subject evidence | `Assessment of a large language model based digital intelligent assistant in assembly manufacturing` | Strongest evidence for an LLM digital intelligent assistant reducing cognitive workload in assembly manufacturing |
| Industrial explainability user study | `User perspectives on AI explainability in aerospace manufacturing: a Card-Sorting study` | Useful for operator mental models and explainability requirements, but not direct LLM override/approval validation |
| Maintenance decision support | `Large Language Model-based Chatbot for Improving Human-Centricity in Maintenance Planning and Operations` | Relevant LLM maintenance-support direction, but limited evidence on workload, trust calibration, or override behavior |
| Cross-sector trust survey | `AI for Decision Support: Balancing Accuracy, Transparency, and Trust Across Sectors` | Useful trust framing, but not industrial in-situ LLM validation |
| Adoption/acceptance survey | `Artificial Intelligence Adoption in SMEs: Survey Based on TOE-DOI Framework` | Captures adoption barriers, not operator-level HITL performance |

## Gap Updates

- Strengthens G7: operator-facing evaluation metrics are not standardized; NASA-TLX, SUS, approval latency, override rate, and trust calibration are missing.
- Strengthens G8: because LLMs remain decision-support layers, the human operator is the actual safety boundary, but operator behavior is not measured.
- Strengthens G10: benchmark suites lack human-factors scorecards for industrial LLMs.
- Strengthens G13: self-improving industrial LLMs require operator correction and approval loops, but those loops have not been empirically validated.
- Strengthens G16: governance assumes human approval, but the capacity, burden, latency, and reliability of that approval are not measured.
- Strengthens G18: production value evidence should include operator-level effects, but those are rarely measured.
- Adds G19: HITL/operator human-factors validation for industrial LLM systems is missing.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260428T015556Z-industrial-llm-operator-human-factors/openalex/manifest.json` | Full export metadata |
| `lit-watch/runs/20260428T015556Z-industrial-llm-operator-human-factors/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260428T015556Z-industrial-llm-operator-human-factors/openalex/all_results_deduped.csv` | 516 deduplicated works plus header |
| `lit-watch/runs/20260428T015556Z-industrial-llm-operator-human-factors/openalex/all_results_deduped.jsonl` | 516 deduplicated raw records |
| `lit-watch/runs/20260428T015556Z-industrial-llm-operator-human-factors/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260428T015556Z-industrial-llm-operator-human-factors/SUMMARY.md` | ARIS execution summary and verdict |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
