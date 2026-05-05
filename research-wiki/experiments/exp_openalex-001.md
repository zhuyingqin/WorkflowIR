---
type: experiment
node_id: exp:openalex-001
title: "OpenAlex Search — LLM Industrial Applications Survey (Initial)"
run_id: "20260427T070858Z-survey-of-large-language-model-applications-in-industry-including-self-evolution"
date: 2026-04-27T07:16:53Z
skill: openalex-search
status: completed
verdict: approved
freshness_window: "2025-04-27 to 2026-04-27"
---

# OpenAlex Search — LLM Industrial Applications Survey (Initial)

**Run ID**: `20260427T070858Z-survey-of-large-language-model-applications-in-industry-including-self-evolution`
**Status**: ✅ Completed

## Query Plan Summary

5 query families targeting LLM applications in industry:

| Query Family | Reported Count | Downloaded | Notes |
|---|---|---|---|
| `industrial_llm_agents` | 714 | 200 | Capped at 200 |
| `self_improving_industrial_llm` | 502 | 200 | Capped at 200 |
| `llm_industrial_concrete_problems` | 195 | 195 | Full export |
| `llm_industrial_trustworthy` | 1030 | 200 | Capped at 200 |
| `llm_industrial_rag_kg` | 164 | 164 | Full export |

**Total deduplicated works**: 832
**Total downloaded rows**: 959

## Query Details

### Shared Constraints
- `from_publication_date:2025-04-27`
- `to_publication_date:2026-04-27`
- `type:article`
- `language:en`
- `is_retracted:false`
- `is_paratext:false`

### Query Families

1. **industrial_llm_agents**: LLM + autonomous agent/multi-agent + manufacturing/industrial
2. **self_improving_industrial_llm**: LLM + self-evolution/self-improvement/feedback + industrial
3. **llm_industrial_concrete_problems**: LLM + predictive maintenance/quality control/fault diagnosis
4. **llm_industrial_trustworthy**: LLM + reliability/hallucination/safety/evaluation/HITL
5. **llm_industrial_rag_kg**: LLM + RAG/knowledge graph/digital twin/industrial

## Noise Diagnosis

- `industrial_llm_agents`: Generic AI adoption papers, broad decision-making systems
- `self_improving_industrial_llm`: Non-industrial self-improvement papers
- `llm_industrial_trustworthy`: Broad trustworthy AI papers without industrial anchor
- `llm_industrial_rag_kg`: GraphRAG surveys mixed with industrial applications

## Top Papers (by citations)

| Title | Citations | DOI |
|-------|-----------|-----|
| DiagLLM: multimodal reasoning with LLM for explainable bearing fault diagnosis | 31 | 10.1007/s11432-024-4333-7 |
| Graph Retrieval-Augmented Generation: A Survey | 27 | 10.1145/3777378 |
| MEGA-RAG: Memory-Augmented Graph Retrieval-Augmented Generation for Streaming Speech towards LLM | 17 | 10.1109/ICME51233.2025.00048 |
| LLM Agents for IoT Security: A Comprehensive Survey | 11 | 10.1109/jiot.2024.3472960 |

## Identified Gaps (for next search)

1. **Domain adaptation**: LoRA, RLHF, fine-tuning LLMs for manufacturing/industrial domains
2. **Edge LLM deployment**: on-device LLMs for factory floor, latency-constrained inference
3. **Physics-informed & causal LLMs**: neuro-symbolic approaches for industrial processes
4. **LLM-driven digital twins**: LLM-controlled digital twins for process optimization
5. **Manufacturing-specific agent architectures**: multi-agent systems tailored to factory workflows

## Reviewer Direction

Build the first evidence map for LLM applications in industry, prioritizing papers that anchor a survey taxonomy rather than narrow single-case demonstrations.

## Output Files

- `openalex/manifest.json` — Full run metadata
- `openalex/query_counts.csv` — Per-query counts
- `openalex/queries/<name>.csv` — Per-query flattened metadata
- `openalex/queries/<name>.jsonl` — Raw OpenAlex work records
- `openalex/all_results_deduped.csv` — Deduplicated works
- `openalex/all_results_deduped.jsonl` — Deduplicated raw records

## Connections

[AUTO-GENERATED from graph/edges.jsonl — do not edit manually]
