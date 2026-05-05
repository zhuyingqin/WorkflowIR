---
type: experiment
node_id: exp:openalex-011
title: "OpenAlex Search - Industrial LLM Agent Workflow Orchestration"
run_id: "20260427T214457Z-industrial-llm-agent-workflow-orchestration"
date: 2026-04-27T21:52:14Z
skill: openalex-search
status: completed
verdict: industrial_llm_agents_are_decision_support_not_orchestrators
freshness_window: "2024-04-27 to 2026-04-27"
---

# OpenAlex Search - Industrial LLM Agent Workflow Orchestration

**Run ID**: `20260427T214457Z-industrial-llm-agent-workflow-orchestration`
**Status**: Completed
**Verdict**: Industrial LLM agents are not yet deployable workflow orchestrators. The evidence is strongest for decision-support assistants, quality/inspection copilots, lab-validated assembly assistants, scheduling prototypes, and one IT-service-layer deployment case.

## Purpose

This run tested whether manufacturing-specific LLM agents have matured from conceptual agentic manufacturing into operational workflow orchestration. It focused on shop-floor workflows, MES/ERP/CMMS/work-order integration, quality inspection, production planning/scheduling, maintenance, technician copilots, human-in-the-loop operations, and multi-agent factory workflows.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-27 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran a dry-run first. The MES/ERP/CMMS family returned zero works with the initial tighter expression, so ARIS broadened it by dropping `work order` and `copilot`. No final family exceeded 300 works, so full export proceeded.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `llm_manufacturing_agent_workflows` | 71 | 71 | 1 |
| `llm_mes_erp_cmms_industrial_copilot` | 2 | 2 | 1 |
| `llm_quality_control_inspection_agent` | 166 | 166 | 1 |
| `llm_production_planning_scheduling_agent` | 101 | 101 | 1 |
| `llm_maintenance_work_order_agent` | 6 | 6 | 1 |

**Total downloaded rows**: 346
**Total deduplicated works**: 300

## Quality Notes

The corpus contains useful signals but also notable noise. Generic AI surveys, deep-learning process-monitoring papers, and broad robotics-agent papers matched some query families without describing LLM agents that orchestrate concrete industrial workflows. Nearly half of the deduplicated corpus has zero citations, which suggests an early 2025-2026 publication wave dominated by surveys, frameworks, and prototypes rather than mature deployments.

## Key Findings

1. No production-deployed autonomous LLM workflow orchestrator was found for live manufacturing operations.
2. No paper describes an LLM agent autonomously creating, routing, executing, and closing MES/ERP/CMMS work orders.
3. The strongest concrete evidence is still human-in-the-loop: an LLM-based digital intelligent assistant for assembly, LLM scheduling prototypes, NDT/X-ray inspection copilots, and an Apollo Tyres GenAI IT-service-management pilot.
4. Quality inspection and non-destructive testing are the most concrete application cluster because human review is natural and safety risk can be bounded.
5. Production planning and scheduling papers show early promise, but they remain prototypes or simulation/lab demonstrations rather than integrated factory workflow managers.
6. MICA and STAR are the most orchestration-like systems found, but both lack production deployment evidence and factory-grade reliability metrics such as OEE, MTBF, scrap rate, or cycle-time reduction.
7. Reliability constraints keep the dominant pattern as LLM copilot plus human approval, not autonomous multi-agent orchestration.

## Representative Papers

| Mechanism | Representative Paper |
|---|---|
| Multi-agent industrial coordination | `MICA: Multi-Agent Industrial Coordination Assistant` |
| Agentic manufacturing survey/framework | `Hybrid agentic AI and multi-agent systems in smart manufacturing` |
| LLM-driven manufacturing simulation | `LLM-driven discrete-event simulation: A generative AI framework for automated model generation, adaptation, and evaluation` |
| Maintenance agent concept | `A Conceptual Design of Industrial Asset Maintenance System by Autonomous Agents Enhanced with ChatGPT` |
| Industry 5.0 agentic AI review | `From Large Language Models to Agentic AI in Industry 5.0` |
| Manufacturing IT middleware | `LLMs as AI Middleware: Unifying Disparate Systems in Manufacturing IT Landscapes` |
| NDT/X-ray inspection copilot | `InsightX Agent: An LMM-Based Agentic Framework with Integrated Tools for Reliable X-Ray NDT` |
| Steelmaking multi-agent routing | `STAR: Steelmaking Task-Aware Routing for Multi-Agent LLM Expert Systems` |
| Assembly assistant | `Design, Development, and Evaluation of LLM-Based Digital Intelligent Assistant in Assembly Manufacturing` |
| Human-robot scheduling | `Leveraging LLMs for Efficient Scheduling in Human-Robot Collaborative Flexible Manufacturing` |
| Semiconductor digital-twin simulation | `Real-to-Sim: Automatic Simulation Model Generation for a Digital Twin in Semiconductor Manufacturing` |
| IT-service industrial deployment | `Generative AI Implementation in Enterprises: Lessons from Enhanced IT Service Management (Apollo Tyres)` |

## Gap Updates

- Updates G5: manufacturing-specific agent architectures are active, but still immature and not production-validated as workflow orchestrators.
- Strengthens G7: workflow-agent evaluation lacks standardized metrics for task completion, workflow latency, human approval burden, safety, reliability, OEE, MTBF, scrap rate, and cycle-time impact.
- Strengthens G8: industrial LLMs remain copilots or decision-support systems rather than autonomous workflow executors.
- Strengthens G10: no cross-domain benchmark suite exists for industrial LLM workflow orchestration across maintenance, quality, scheduling, MES/ERP/CMMS, and production KPIs.
- Adds G15: MES/ERP/CMMS/work-order LLM orchestration is essentially unexplored; the focused query returned only two papers and no concrete LLM agent integration.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260427T214457Z-industrial-llm-agent-workflow-orchestration/openalex/manifest.json` | Full run metadata and API params |
| `lit-watch/runs/20260427T214457Z-industrial-llm-agent-workflow-orchestration/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260427T214457Z-industrial-llm-agent-workflow-orchestration/openalex/all_results_deduped.csv` | 300 deduplicated works plus header |
| `lit-watch/runs/20260427T214457Z-industrial-llm-agent-workflow-orchestration/openalex/all_results_deduped.jsonl` | 300 deduplicated raw records |
| `lit-watch/runs/20260427T214457Z-industrial-llm-agent-workflow-orchestration/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260427T214457Z-industrial-llm-agent-workflow-orchestration/SUMMARY.md` | Run summary and survey implications |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
