---
type: experiment
node_id: exp:openalex-003
title: "OpenAlex Search — LLM Industry Trustworthy Tightening (Approved)"
run_id: "20260427T074523Z-llm-industry-trustworthy-tightening"
date: 2026-04-27T07:45:23Z
skill: openalex-search
status: completed
verdict: approved
freshness_window: "2025-04-27 to 2026-04-27"
---

# OpenAlex Search — LLM Industry Trustworthy Tightening (Approved)

**Run ID**: `20260427T074523Z-llm-industry-trustworthy-tightening`
**Status**: ✅ Approved with notes

## Query Plan Summary

8 named query families using `title_and_abstract.search` OpenAlex filter syntax. This was a tightening pass focusing on trustworthy AI in industrial settings.

| Query Family | Dry-Run | Downloaded | Status |
|---|---|---|---|
| `agentic_smart_manufacturing` | 12 | 12 | No cap |
| `llm_self_improving_industrial` | 65 | 65 | No cap |
| `llm_predictive_prescriptive_maintenance` | 186 | 186 | No cap |
| `llm_kg_rag_industrial` | 206 | 200 | Capped |
| `trustworthy_eval_monitoring_industrial` | 209 | 200 | Capped |
| `trustworthy_hitl_industrial_agents` | 124 | 124 | No cap |
| `trustworthy_hallucination_industrial_rag` | 527 | 200 | Capped |
| `trustworthy_safety_critical_industrial` | 32 | 32 | No cap |

**Total deduplicated works**: 886
**Total downloaded rows**: 1,019

## Dry-Run → Full Export Evolution

| Round | Key Change | Families Still Over 300 |
|---|---|---|
| Round 1 (broad `search`) | Initial expressions | 6/8 above 300 |
| Round 2 (all `title_and_abstract.search`) | Switched to filter-based precision | 3/8 above 300 |
| Round 3 | Removed broad ORs, added domain anchors | 2/8 above 300 |
| Round 4 | Tightened eval phrase; narrowed hallucination | 1/8 above 300 |

Stop criteria met: ≥3 families under 300 ✅ (7/8 pass), ≥1 trustworthy family under 150 ✅ (2/8 pass: HITL=124, safety=32).

## Search Formulas

```
agentic_smart_manufacturing:
  filter: title_and_abstract.search:"agentic LLM" OR "autonomous agent",
          title_and_abstract.search:"smart manufacturing" OR "industrial automation" OR "factory robot"

llm_self_improving_industrial:
  filter: title_and_abstract.search:"large language model" OR LLM,
          title_and_abstract.search:"self-improving" OR "self-improvement" OR "self-supervised improvement"

llm_predictive_prescriptive_maintenance:
  filter: title_and_abstract.search:"large language model" OR LLM,
          title_and_abstract.search:"predictive maintenance" OR "prescriptive maintenance" OR "fault diagnosis"

llm_kg_rag_industrial:
  filter: title_and_abstract.search:"large language model" OR LLM,
          title_and_abstract.search:"knowledge graph" OR RAG OR "retrieval-augmented",
          title_and_abstract.search:manufacturing OR industrial

trustworthy_eval_monitoring_industrial:
  filter: title_and_abstract.search:"large language model" OR LLM,
          title_and_abstract.search:"evaluation benchmark" OR validation,
          title_and_abstract.search:manufacturing OR maintenance OR "quality control"

trustworthy_hitl_industrial_agents:
  filter: title_and_abstract.search:"large language model" OR LLM,
          title_and_abstract.search:"human-in-the-loop" OR auditability,
          title_and_abstract.search:manufacturing OR automation OR factory OR maintenance

trustworthy_hallucination_industrial_rag:
  filter: title_and_abstract.search:"large language model" OR LLM,
          title_and_abstract.search:hallucination,
          title_and_abstract.search:RAG OR "knowledge graph"

trustworthy_safety_critical_industrial:
  filter: title_and_abstract.search:"large language model" OR LLM,
          title_and_abstract.search:safety OR risk OR verification,
          title_and_abstract.search:"industrial deployment" OR factory OR "smart manufacturing" OR "process control"
```

## Noise Diagnosis

- **`trustworthy_hallucination_industrial_rag`**: Captures non-industrial hallucination papers (healthcare RAG, code generation). Top export includes `MEGA-RAG` (public health) and `LLM Hallucinations in Code Generation`. Recommend splitting into strict manufacturing-only hallucination + RAG subfamily.
- **`llm_self_improving_industrial`**: Lacks manufacturing/industrial anchor filter, pulling in general LLM self-improvement papers (3D printing, sentiment analysis). Needs `title_and_abstract.search:manufacturing OR industrial` constraint.
- **`trustworthy_eval_monitoring_industrial`**: Minor noise from business-process papers without hard industrial context. Otherwise solid.
- **`llm_kg_rag_industrial`**: Captures broad GraphRAG surveys as expected; specific industrial papers like `Verification and Validation of LLM-RAG for Industrial Automation` (IEEE AI-Test 2025) are highly relevant.

## Top Papers Per Family (highest citation)

| Family | Title | Year | Citations | DOI |
|---|---|---|---|---|
| `agentic_smart_manufacturing` | AI Agents and Agentic AI–navigating a plethora of concepts for future manufacturing | 2025 | 16 | 10.1016/j.jmsy.2025.08.017 |
| `llm_self_improving_industrial` | Evaluating zero-shot multilingual aspect-based sentiment analysis with large language models | 2025 | 15 | 10.1007/s13042-025-02711-z |
| `llm_predictive_prescriptive_maintenance` | DiagLLM: multimodal reasoning with LLM for explainable bearing fault diagnosis | 2025 | 31 | 10.1007/s11432-024-4333-7 |
| `llm_kg_rag_industrial` | Graph Retrieval-Augmented Generation: A Survey | 2025 | 27 | 10.1145/3777378 |
| `trustworthy_eval_monitoring_industrial` | Few-shot and chain-of-thought prompting for equipment maintenance knowledge graphs | 2026 | 5 | 10.1016/j.knosys.2026.115266 |
| `trustworthy_hitl_industrial_agents` | Augmenting Intelligent Process Automation through Generative AI for Human-in-the-Loop | 2025 | 3 | 10.1016/j.dte.2025.100071 |
| `trustworthy_hallucination_industrial_rag` | LLM Hallucinations in Practical Code Generation: Phenomena, Mechanism, and Mitigation | 2025 | 49 | 10.1145/3728894 |
| `trustworthy_safety_critical_industrial` | LLM-Guided risk-sensitive reinforcement learning for smart factories | 2025 | 1 | 10.1016/j.eswa.2025.130093 |

## Survey Taxonomy Candidates

1. **Agentic Manufacturing Systems** — multi-agent LLM coordination, autonomous robot planning, factory automation
2. **Industrial RAG & Knowledge Graphs** — LLM + KG/RAG for manufacturing knowledge bases, digital twins
3. **Predictive & Prescriptive Maintenance** — fault diagnosis, condition monitoring, remaining useful life estimation
4. **Trustworthy Deployment — Eval & Monitoring** — benchmarks, validation frameworks, production monitoring
5. **Trustworthy Deployment — Safety & HITL Agents** — human-in-the-loop control, risk-sensitive RL, verification
6. **Self-Improving Industrial LLMs** — online/continual learning, self-supervised improvement in operational settings

## Gaps to Search Next

- **Domain adaptation**: LoRA, RLHF, fine-tuning LLMs for manufacturing/industrial domains
- **Edge LLM deployment**: on-device LLMs for factory floor, latency-constrained industrial inference
- **Physics-informed & causal LLMs**: neuro-symbolic approaches, physics-guided LLM for industrial processes
- **LLM-driven digital twins**: LLM-controlled or LLM-simulated digital twins for process optimization

## Output Files

| File | Description |
|---|---|
| `openalex/manifest.json` | Full run metadata, API params, timestamps |
| `openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `openalex/queries/<name>.csv` | Flattened metadata per query |
| `openalex/queries/<name>.jsonl` | Raw OpenAlex work records per query |
| `openalex/all_results_deduped.csv` | Deduplicated works across all queries |
| `openalex/all_results_deduped.jsonl` | Deduplicated raw records with `matched_queries` |
| `openalex_queries.json` | Reproducible query plan |
| `reviewer_direction.md` | Codex reviewer decision |

## Connections

[AUTO-GENERATED from graph/edges.jsonl — do not edit manually]
