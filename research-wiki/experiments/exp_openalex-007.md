---
type: experiment
node_id: exp:openalex-007
title: "OpenAlex Search — Edge/SLM Industrial Deployment"
run_id: "20260427T174756Z-edge-slm-industrial-deployment"
date: 2026-04-27T17:55:00Z
skill: openalex-search
status: completed_with_broad_families
verdict: edge_native_deployment_gap_confirmed
freshness_window: "2024-04-27 to 2026-04-27"
---

# OpenAlex Search — Edge/SLM Industrial Deployment

**Run ID**: `20260427T174756Z-edge-slm-industrial-deployment`
**Status**: Completed with broad query families
**Verdict**: G2 confirmed open — industrial LLM deployment is cloud-predominant with edge augmentation, not yet edge-native for hard real-time control

## Purpose

This run tested whether industrial LLMs or small language models can credibly run near the factory floor under latency, memory, energy, privacy, reliability, and network constraints. It focused on edge deployment, SLM/model compression, edge-cloud orchestration, real-time industrial control, and edge reliability evaluation.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-27 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran multiple dry-run refinement rounds and exported the final query families into `openalex/`.

| Query Family | Reported | Downloaded | Notes |
|---|---:|---:|---|
| `edge_llm_factory_floor_deployment` | 405 | 405 | Above the 300 target, but tightened from 2701 and high-signal for edge/factory deployment |
| `industrial_slm_tiny_llm_deployment` | 1709 | 1709 | Broad/noisy; SLM/compression terms overlap heavily with SLAM, CV, DNN pruning, and general industrial edge AI |
| `edge_cloud_industrial_llm_orchestration` | 415 | 415 | Above the 300 target, but useful for edge-cloud, privacy, federated, and Industry 4.0 deployment patterns |
| `real_time_llm_industrial_control_latency` | 303 | 303 | Just above the 300 target; strongest for CNC/PLC/SCADA/robot real-time constraints |
| `edge_llm_industrial_reliability_evaluation` | 74 | 74 | Focused set for edge reliability/evaluation/resource metrics |

**Total downloaded rows**: 2906
**Total deduplicated works**: 2640

## Compliance Note

This run is valuable as an exploratory deployment map, but it is not a fully tightened final search formula. Four families remained above the requested 300-work target. The `industrial_slm_tiny_llm_deployment` family is especially noisy because OpenAlex search conflates small-language-model/compression concepts with SLAM, computer vision, DNN pruning, industrial communications, and general edge AI.

## Key Findings

1. G2 is confirmed open: the literature shows cloud-predominant industrial LLM systems with edge augmentation, not mature edge-native LLM/SLM deployment for factory-floor real-time control.
2. Edge-cloud orchestration, federated LLMs, privacy-preserving knowledge graphs, and end-edge-cloud industrial architectures are active, but mostly architectural or decision-support oriented.
3. Real-time industrial LLM work is strongest in monitoring and diagnostics: CNC monitoring, SCADA tag generation, fault diagnosis, robot speech control, and PLC/control-code support.
4. SLM/compression evidence is weak for true language models; most compression results are actually vision/DNN models for industrial detection or IIoT offloading.
5. Reliability/evaluation for edge industrial LLMs is sparse; there is no standardized benchmark for latency, memory, energy, network degradation, fail-safe behavior, or on-device safety.
6. Human-in-the-loop remains the dominant operational pattern: LLMs support diagnostics, AR-assisted planning, conversational monitoring, and speech interfaces rather than autonomous safety-critical control.

## Representative Papers

| Topic | Representative Paper |
|---|---|
| Edge/factory architecture | `Embodied Intelligence Empowering Customized Manufacturing: Architecture, Opportunities, and Challenges` |
| Smart manufacturing agents | `Agent technologies in smart manufacturing: A comprehensive review of evolution, architectures, and edge-cloud deployment` |
| CNC real-time monitoring | `ChatCNC: Conversational machine monitoring via large language model and real-time data retrieval augmented generation` |
| Industrial robot control | `LLM-driven agent for speech-enabled control of industrial robots: A case study in snow-crab quality inspection` |
| Privacy/federated deployment | `A Review of Federated Large Language Models for Industry 4.0` |
| Industrial KG privacy | `Unlocking Large Language Model Power in Industry: Privacy-Preserving Collaborative Creation of Knowledge Graph` |
| IIoT offloading/compression | `Joint Task Offloading, DNN Pruning, and Computing Resource Allocation for Fault Detection With Dynamic Constraints in Industrial IoT` |
| Edge reliability/HITL | `You are my eyes: Integrating human intelligence and LLMs in AR-assisted motion planning for industrial mobile robots` |

## Gap Updates

- Updates G2 from open to confirmed open gap: local/edge-native LLM or SLM deployment for factory-floor systems remains immature.
- Strengthens G8: edge deployment does not yet solve LLM-as-controller readiness; most work is monitoring, diagnosis, planning, or conversational support.
- Strengthens G10: edge industrial LLM evaluation lacks comparable latency, energy, memory, reliability, and fail-safe benchmarks.
- Adds G11: production-grade, safety-certified edge-native LLM/SLM controllers for industrial systems are absent; current systems remain edge-augmented rather than edge-native.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260427T174756Z-edge-slm-industrial-deployment/openalex/manifest.json` | Full run metadata and API params |
| `lit-watch/runs/20260427T174756Z-edge-slm-industrial-deployment/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260427T174756Z-edge-slm-industrial-deployment/openalex/all_results_deduped.csv` | 2640 deduplicated works plus header |
| `lit-watch/runs/20260427T174756Z-edge-slm-industrial-deployment/openalex/all_results_deduped.jsonl` | 2640 deduplicated raw records |
| `lit-watch/runs/20260427T174756Z-edge-slm-industrial-deployment/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260427T174756Z-edge-slm-industrial-deployment/SUMMARY.md` | Run summary and implications |

## Connections

[AUTO-GENERATED from graph/edges.jsonl — do not edit manually]
