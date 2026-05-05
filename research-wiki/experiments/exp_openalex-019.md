---
type: experiment
node_id: exp:openalex-019
title: "OpenAlex Search - Industrial LLM Scheduling, Process Planning, and Operations Optimization"
run_id: "20260428T035157Z-industrial-llm-scheduling-process-planning-optimization"
date: 2026-04-28T03:59:53Z
skill: openalex-search
status: completed
verdict: industrial_llm_planning_orchestrator_not_autonomous_optimizer
freshness_window: "2024-04-27 to 2026-04-28"
---

# OpenAlex Search - Industrial LLM Scheduling, Process Planning, and Operations Optimization

**Run ID**: `20260428T035157Z-industrial-llm-scheduling-process-planning-optimization`
**Status**: Completed
**Verdict**: Industrial LLM planning systems are mainly formulation generators, solver orchestrators, natural-language interfaces, and explainers rather than autonomous optimization solvers with validated production deployment.

## Purpose

This run tested whether LLMs solve concrete industrial planning and optimization problems such as job-shop scheduling, process route generation, production planning, inventory/logistics decisions, and constrained resource allocation, or whether they mainly wrap traditional optimization solvers, MES/ERP dashboards, or decision-support reports.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-28 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran dry-runs first and tightened all query families above 300 works before full export. One OpenAlex filter attempt using `title_and_abstract.search` failed with HTTP 400, then the executor corrected to valid `abstract.search` filters.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `industrial_llm_production_scheduling` | 34 | 34 | 1 |
| `llm_shop_floor_dispatching_optimization` | 20 | 20 | 1 |
| `llm_process_planning_manufacturing` | 83 | 83 | 1 |
| `llm_supply_chain_inventory_industrial_planning` | 4 | 4 | 1 |
| `llm_constraint_optimization_manufacturing_operations` | 25 | 25 | 1 |

**Total downloaded rows**: 166
**Total deduplicated works**: 142

## Query Tightening Notes

- Initial dry-run counts were 1297, 20, 4436, 488, and 2191 works.
- Production scheduling, process planning, supply-chain/inventory, and constraint-optimization families required tightening.
- Supply-chain/inventory was reduced from 488 to 4 using a strict three-way `abstract.search` AND filter. The resulting 4 papers are high-precision but likely under-sample broader supply-chain literature.
- The final corpus included notable noise in shop-floor dispatching and constraint-optimization families, including general smart-city, medical, engineering design, and topology-optimization papers.

## Key Findings

1. LLMs primarily generate formulations, code, process chains, constraints, heuristics, or explanations. External MILP/ILP, DRL, genetic algorithms, ACO/VNS, heuristic dispatching rules, and simulation engines remain the real optimizers.
2. The strongest planning contributions include solver-ready formulation generation, LLM-based multi-agent scheduling chains, LLM-assisted evolutionary scheduling, CAPP-GPT, process-chain generation, and automated constraint specification for APS.
3. Some scheduling work is practically meaningful: one HRC flexible-manufacturing paper reports 21.52% average makespan reduction across 54 real-world HRC scenarios via local fine-tuned LLM and population self-evolution.
4. Production deployment evidence remains scarce. The strongest real field signal is a textile SME supply-chain/demand-planning field study, but it uses ML and Monte Carlo rather than an explicit LLM core.
5. Self-evolution is rare. Only a small number of papers show population self-evolution, human feedback for reward shaping, self-prompting, or conversational replanning. No paper demonstrates online learning from production outcomes with approval, rollback, and safety-case updates.
6. A CNC G-code optimization paper reports that ChatGPT removed essential safety commands, underscoring that LLM-generated industrial control or planning code requires human review and domain-specific safety constraints.
7. Supply-chain and inventory planning remain under-covered for explicit LLM systems in this run.

## Representative Papers

| Problem Class | Representative Paper | Takeaway |
|---|---|---|
| Digital manufacturing optimization | `Business optimization for digital manufacturing: A fine-tuned large language model approach` | Fine-tuned LLM generates solver-ready LP/MILP formulations with >95% success and execution-based validation |
| Flexible job-shop scheduling | `MASC: Large language model-based multi-agent scheduling chain for flexible job shop scheduling problem` | LLM multi-agent scheduling chain targets FJSP makespan |
| HRC scheduling | `Leveraging large language models for efficient scheduling in Human-Robot collaborative flexible manufacturing systems` | Local LLM generates heuristic dispatching rules with population self-evolution and reported makespan reduction |
| Process planning | `CAPP-GPT: A computer-aided process planning-generative pretrained transformer framework for smart manufacturing` | LLM + optimization/ML supports CAPP, toolpath/process parameter adaptation, and process signatures |
| Process-chain generation | `Large language models for high-level computer-aided process planning in a distributed manufacturing paradigm` | GPT-style sequence model generates alternative process chains from part encodings |
| APS constraint specification | `Automated Constraint Specification for Job Scheduling by Regulating Generative Model With Domain-Specific Representation` | LLM is regulated by domain-specific representation to generate reliable constraints for scheduling solvers |
| Satisficing tradeoffs | `Generative AI for Interpretable Satisficing Solution Design in Manufacturing` | LLM explains high-dimensional tradeoffs for steel hot-rod rolling rather than solving optimization directly |
| Safety caution | CNC G-code optimization with ChatGPT | ChatGPT removed safety-critical G-code commands, demonstrating need for HITL verification |

## Gap Updates

- Strengthens G5/G15: planning and MES/APS/work-order orchestration have LLM-assisted formulations and interfaces, but not production-autonomous planning loops.
- Strengthens G7/G10: industrial LLM benchmarks lack OR metrics such as makespan, tardiness, constraint violations, optimality gaps, solver success, schedule repair, and production KPI impact.
- Strengthens G8: LLMs remain formulation generators and solver orchestrators rather than autonomous industrial controllers or optimizers.
- Strengthens G13: self-evolution in planning is limited to population evolution, human feedback, or prompt iteration; no online production learning loop is validated.
- Strengthens G16: safe optimization needs auditable constraints, human approval, rollback, and domain-specific representations.
- Strengthens G18: production deployment and KPI evidence remain sparse for LLM-driven scheduling/planning.
- Adds G23: LLM-enabled industrial planning and optimization lacks production-grade autonomous constrained optimization.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260428T035157Z-industrial-llm-scheduling-process-planning-optimization/openalex/manifest.json` | Full export metadata |
| `lit-watch/runs/20260428T035157Z-industrial-llm-scheduling-process-planning-optimization/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260428T035157Z-industrial-llm-scheduling-process-planning-optimization/openalex/all_results_deduped.csv` | 142 deduplicated works plus header |
| `lit-watch/runs/20260428T035157Z-industrial-llm-scheduling-process-planning-optimization/openalex/all_results_deduped.jsonl` | 142 deduplicated raw records |
| `lit-watch/runs/20260428T035157Z-industrial-llm-scheduling-process-planning-optimization/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260428T035157Z-industrial-llm-scheduling-process-planning-optimization/SUMMARY.md` | ARIS execution summary and verdict |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
