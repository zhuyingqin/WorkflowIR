---
type: experiment
node_id: exp:openalex-017
title: "OpenAlex Search - Industrial LLM Sensor-Grounded PHM and Fault Diagnosis"
run_id: "20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis"
date: 2026-04-28T03:01:14Z
skill: openalex-search
status: completed
verdict: industrial_llm_sensor_phm_mostly_explanation_layer
freshness_window: "2024-04-27 to 2026-04-28"
---

# OpenAlex Search - Industrial LLM Sensor-Grounded PHM and Fault Diagnosis

**Run ID**: `20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis`
**Status**: Completed
**Verdict**: Industrial LLMs for sensor-grounded fault diagnosis, PHM, predictive maintenance, anomaly detection, and operator maintenance support are mostly explanation or workflow-assistant layers on top of conventional sensor-processing models. Direct sensor-to-LLM diagnostic systems exist but are rare, lab-benchmark based, and not production validated.

## Purpose

This run tested whether industrial LLMs solve concrete sensor-backed industrial problems such as machine fault diagnosis, process monitoring, quality inspection, maintenance triage, RUL reasoning, alarm explanation, and operator guidance, or whether they mainly summarize and explain outputs from conventional PHM/deep-learning systems.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-28 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran dry-runs first, found several overly broad families, then tightened all query families above 300 works before full export.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `industrial_llm_sensor_fault_diagnosis` | 10 | 10 | 1 |
| `llm_predictive_maintenance_machinery_health_monitoring` | 15 | 15 | 1 |
| `multimodal_llm_manufacturing_quality_inspection` | 15 | 15 | 1 |
| `industrial_llm_anomaly_detection_process_monitoring` | 33 | 33 | 1 |
| `phm_llm_operator_maintenance_agent` | 87 | 87 | 1 |

**Total downloaded rows**: 160
**Total deduplicated works**: 157

## Query Tightening Notes

- Initial dry-run counts were 480, 616, 303, 1952, and 87 works.
- The first tightening attempt over-constrained two families, reducing predictive maintenance to 2 works and anomaly detection to 0 works.
- Final query-specific filters balanced recall and precision, yielding final counts of 10, 15, 15, 33, and 87.
- The process-anomaly family still retained persistent non-industrial IT/cloud/medical noise, showing that `industrial anomaly detection` remains semantically broad in OpenAlex.

## Key Findings

1. Genuine sensor-to-LLM diagnostic integration is rare. KG-SR-LLM is the clearest example, transforming vibration time-series features into semantic sequences and using LoRA-prompted LLM reasoning for cross-domain bearing fault diagnosis.
2. The best direct evidence remains lab-dataset validation rather than production deployment. KG-SR-LLM reports 98.36% average diagnostic accuracy across 11 public datasets and a 9.22% improvement over classical deep-learning baselines, but not field deployment.
3. Multimodal quality-inspection work is emerging through vision-language models and zero-shot anomaly-detection pipelines, but these are mostly benchmark/prototype studies.
4. Predictive-maintenance and machinery-health papers are still dominated by conventional deep learning, federated learning, and IIoT frameworks. LLMs often appear as report generators, explainers, or workflow assistants rather than the core sensor model.
5. PHM/operator-agent results are heavily survey and review dominated. The strongest papers describe opportunities, taxonomies, or digital-twin ecosystems rather than validated operator-facing maintenance agents.
6. No run evidence showed active learning, operator-correction loops, runtime drift adaptation, continuous memory growth, or update-approval workflows for LLM-driven sensor/PHM systems.
7. No production system reported MTBF, downtime, maintenance-cost impact, false-alarm reduction, operator override rate, approval latency, or real plant KPI outcomes for an LLM-driven sensor-PHM system.

## Representative Papers

| Problem Class | Representative Paper | Takeaway |
|---|---|---|
| Bearing fault diagnosis | `KG-SR-LLM: Knowledge-Guided Semantic Representation and Large Language Model Framework for Cross-Domain Bearing Fault Diagnosis` | Strongest direct sensor-to-LLM signal; vibration time-series features are converted into semantic text sequences; 98.36% average accuracy across 11 datasets |
| Machine fault diagnosis | `Multimodal data-enabled large model for machine fault diagnosis towards intelligent operation and maintenance` | Directly targets multimodal machine fault diagnosis and O&M decision support, but the evidence remains early |
| Real-time rail fault diagnosis | `Intelligent Fault Diagnosis System for Running Gear of High-Speed Trains` | Demonstrates real-time sensor diagnosis at 70.3 ms inference, but uses TimesNet rather than an LLM |
| Industrial quality inspection | `A unified vision-language model for cross-product defect detection in glove manufacturing` | Shows VLM promise for cross-product defect detection, but still benchmark/prototype level |
| Zero-shot image anomaly detection | `Automatic Prompt Generation and Grounding Object Detection for Zero-Shot Image Anomaly Detection` | Uses foundation-model prompting for industrial defect detection, not production PHM |
| PHM/diagnostics review | `Large Models for Machine Monitoring and Fault Diagnostics: Opportunities, Challenges and Future Direction` | Finds LLM diagnostics concentrated in in-context learning, fine-tuning, RAG, multimodal, and time-series approaches, with many open challenges |

## Gap Updates

- Strengthens G7: sensor/PHM LLM evaluation lacks standard metrics for false alarms, time-to-detect, RUL error, drift adaptation, operator correction, and production KPI impact.
- Strengthens G8: most systems remain explanation or assistant layers, not validated sensor-grounded operational actors.
- Strengthens G10: no cross-domain benchmark suite covers industrial LLM fault diagnosis, PHM, multimodal inspection, RUL, and process anomaly monitoring.
- Strengthens G13: self-evolving industrial LLMs are absent in sensor/PHM settings; no active learning, runtime drift adaptation, memory growth, or operator-correction loop was found.
- Strengthens G18: production deployment and KPI evidence is still absent for LLM-driven sensor/PHM systems.
- Adds G21: sensor-grounded industrial LLM diagnostics and PHM remain immature, lab-benchmark based, and mostly conventional PHM plus LLM explanation wrappers.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis/openalex/manifest.json` | Full export metadata |
| `lit-watch/runs/20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis/openalex/all_results_deduped.csv` | 157 deduplicated works plus header |
| `lit-watch/runs/20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis/openalex/all_results_deduped.jsonl` | 157 deduplicated raw records |
| `lit-watch/runs/20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis/SUMMARY.md` | ARIS execution summary and verdict |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
