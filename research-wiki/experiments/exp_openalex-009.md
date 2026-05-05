---
type: experiment
node_id: exp:openalex-009
title: "OpenAlex Search - Self-Evolving Industrial LLM Agents"
run_id: "20260427T205926Z-self-evolving-industrial-llm-agents"
date: 2026-04-27T21:05:41Z
skill: openalex-search
status: completed
verdict: weak_external_self_improvement_not_true_self_evolution
freshness_window: "2024-04-27 to 2026-04-27"
---

# OpenAlex Search - Self-Evolving Industrial LLM Agents

**Run ID**: `20260427T205926Z-self-evolving-industrial-llm-agents`
**Status**: Completed
**Verdict**: Industrial LLM self-improvement is mostly weak, external, and human-mediated. True production self-evolution, where an LLM continuously updates itself from live industrial feedback, is essentially absent.

## Purpose

This run tested whether industrial LLM systems actually improve through operator feedback, live process feedback, digital-twin simulation, active learning, persistent memory, or online adaptation. It was designed to support the survey section on self-evolution and to distinguish true LLM-level self-improvement from static deployment plus external evaluation.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-27 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran dry-run first, tightened the only broad family above 300, and then executed full export.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `continual_learning_industrial_llm` | 15 | 15 | 1 |
| `operator_feedback_industrial_llm` | 1 | 1 | 1 |
| `memory_augmented_industrial_llm_agent` | 11 | 11 | 1 |
| `digital_twin_feedback_industrial_llm` | 141 | 141 | 1 |
| `active_learning_industrial_llm_maintenance` | 142 | 142 | 1 |

**Total downloaded rows**: 310
**Total deduplicated works**: 236

## Tightening Notes

The first dry-run found `digital_twin_feedback_industrial_llm` at 401 reported works. ARIS tightened it from `"large language model" digital twin simulation feedback industrial process manufacturing maintenance adaptive` to `"large language model" "digital twin" simulation feedback industrial manufacturing fault diagnosis maintenance`, reducing the family to 141. All final families were under 300 before full export.

## Key Findings

1. No production industrial LLM was found that autonomously updates its own weights in real time from live process feedback.
2. The strongest self-improvement evidence is external: HITL feedback, RLHF-style expert correction, RAG or knowledge-base updates, active-learning sample selection, synthetic data generation, downstream model retraining, and digital-twin simulation loops.
3. Operator-feedback evidence is very sparse: the focused operator-feedback family returned only 1 work, supporting the prior G6 conclusion that explicit industrial feedback loops remain rare.
4. Digital-twin feedback is the richest conceptual route to self-evolving industrial agents, but implementations remain proof-of-concept or simulation-stage.
5. Memory-augmented systems exist, including coal-mine safety and cognitive O&M examples, but memory is usually an external experience store or knowledge graph rather than automatic LLM weight adaptation.
6. Active learning is the most deployable practical mechanism for fault diagnosis and predictive maintenance, but the improvement typically occurs in fault classifiers, data pipelines, or prompt/RAG layers rather than the LLM itself.
7. HITL oversight remains mandatory because safety certification, hallucination risk, and accountability constraints make autonomous self-evolution unsafe in many industrial environments.

## Representative Papers

| Mechanism | Representative Paper |
|---|---|
| Online adaptation | `Adaptive Multi-Objective Reinforcement Learning for Real-Time Manufacturing Robot Control` |
| Adaptive agent architecture | `Hybrid agentic AI and multi-agent systems in smart manufacturing` |
| HITL feedback | `Clever Hans in the Loop? A Critical Examination of ChatGPT in a Human-in-the-Loop Framework for Machinery Functional Safety Risk Analysis` |
| Industrial automation robustness | `Industrial Process Automation Through Machine Learning and OPC-UA: A Systematic Literature Review` |
| Multi-level HITL adaptation | `Co-design of communication, computing and control for real-time interactions in industrial cyber-physical systems` |
| Persistent industrial memory | `An Embodied Intelligence System for Coal Mine Safety Assessment Based on Multi-Level Large Language Models` |
| Adaptive PHM roadmap | `Large Models for Machine Monitoring and Fault Diagnostics` |
| Knowledge-guided adaptation | `KG-SR-LLM: Knowledge-Guided Semantic Representation and LLM Framework for Cross-Domain Bearing Fault Diagnosis` |
| Digital-twin self-evolution | `Agent-based digital twins for collaborative machine intelligence solutions` |
| Cognitive O&M digital twin | `From Forecasting to Foresight: Building an Autonomous O&M Brain for the New Power System Based on a Cognitive Digital Twin` |
| Simulation feedback | `LLM-driven discrete-event simulation: A generative AI framework for automated model generation, adaptation, and evaluation in manufacturing` |
| Active learning for FDD | `Multimodal LLM-Based Fault Detection and Diagnosis in Context of Industry 4.0` |
| RLHF for power dispatch logs | `Improving the Precision of Hidden Danger Recognition in Power Dispatch Duty Logs through RLHF Multi-round Human Feedback Mechanism` |

## Gap Updates

- Strengthens G1: industrial adaptation exists through prompt tuning, LoRA, active learning, and RAG/knowledge-base updates, but most systems are not self-evolving after deployment.
- Strengthens G6: explicit operator/HITL/preference feedback loops remain very sparse for industrial LLMs.
- Strengthens G7/G10: evaluation of adaptation mechanisms is missing; papers rarely measure whether feedback, memory growth, or digital-twin synchronization improves industrial KPIs over time.
- Adds G13: true self-evolving industrial LLMs are absent; current self-improvement is mostly external, batch-style, and human-supervised.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260427T205926Z-self-evolving-industrial-llm-agents/openalex/manifest.json` | Full run metadata and API params |
| `lit-watch/runs/20260427T205926Z-self-evolving-industrial-llm-agents/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260427T205926Z-self-evolving-industrial-llm-agents/openalex/all_results_deduped.csv` | 236 deduplicated works plus header |
| `lit-watch/runs/20260427T205926Z-self-evolving-industrial-llm-agents/openalex/all_results_deduped.jsonl` | 236 deduplicated raw records |
| `lit-watch/runs/20260427T205926Z-self-evolving-industrial-llm-agents/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260427T205926Z-self-evolving-industrial-llm-agents/SUMMARY.md` | Run summary and survey implications |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
