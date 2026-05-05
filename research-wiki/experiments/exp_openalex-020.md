---
type: experiment
node_id: exp:openalex-020
title: "OpenAlex Search - Industrial VLM/LLM Quality Inspection and Defect Detection"
run_id: "20260428T041957Z-industrial-vlm-quality-inspection-defect-detection"
date: 2026-04-28T04:26:26Z
skill: openalex-search
status: completed
verdict: industrial_vlm_quality_inspection_mostly_explanation_layer
freshness_window: "2024-04-28 to 2026-04-28"
---

# OpenAlex Search - Industrial VLM/LLM Quality Inspection and Defect Detection

**Run ID**: `20260428T041957Z-industrial-vlm-quality-inspection-defect-detection`
**Status**: Completed
**Verdict**: Industrial LLM/VLM quality-inspection systems are mostly report, explanation, prompt-generation, and semantic-alignment layers over conventional vision backbones rather than production-grade inspection agents.

## Purpose

This run tested whether industrial LLMs, multimodal LLMs, and VLMs solve concrete quality problems such as visual inspection, defect detection, defect localization, root-cause explanation, nonconformance reporting, and rework guidance, or whether they mainly wrap conventional computer-vision defect detectors with natural-language explanations.

## Query Plan Summary

The run used a 2024-04-28 to 2026-04-28 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran a dry-run first; all query families were under the 300-work threshold, so no tightening was required.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `industrial_vlm_quality_inspection` | 5 | 5 | 1 |
| `llm_quality_control_defect_explanation` | 20 | 20 | 1 |
| `multimodal_llm_visual_anomaly_detection` | 25 | 25 | 1 |
| `industrial_vlm_defect_detection_datasets` | 34 | 34 | 1 |
| `llm_root_cause_quality_rework` | 3 | 3 | 1 |

**Total downloaded rows**: 87
**Total deduplicated works**: 82

## Key Findings

1. The strongest corpus signal is that LLMs/VLMs add semantic alignment, prompt generation, report generation, explanation, or reasoning on top of YOLO, CNN, CLIP, DINOv2, SAM, Grounding DINO, fuzzy inference, RAG, KG, or other non-LLM backbones.
2. Core defect scoring and localization usually remain in conventional visual models. VLMs help with zero-shot/few-shot transfer and natural-language interpretation, but they are rarely the production decision authority.
3. Spatial grounding is still weak. One additive-manufacturing study reports GPT-4o classification accuracy of 91.42%, while localization reaches only 16.27%, highlighting the gap between defect naming and actionable defect location.
4. Real factory deployment evidence is sparse. Most works validate on MVTec-AD, VisA, WM-811K, NEU-DET, or similar benchmarks rather than long-running production lines.
5. Human-in-the-loop validation, corrected-label learning, drift adaptation, uncertainty escalation, audit trails, and quality-system compliance are nearly absent.
6. Root-cause and rework guidance are especially thin. Only a few works connect inspection outputs to causal knowledge graphs, Ishikawa-style explanations, or repair/reuse/recycle decisions.
7. Self-improvement remains essentially unvalidated. The corpus shows little evidence that operator corrections, new defect modes, rework outcomes, or production drift are used to safely update the inspection system.

## Representative Papers

| Problem Class | Representative Paper | Takeaway |
|---|---|---|
| Wafer and semiconductor inspection | `YOLO-LA: Prototype-Based Vision-Language Alignment for Silicon Wafer Defect Pattern Detection` | Uses frozen YOLO plus text encoder alignment for wafer bin map defect patterns; suitable for real-time inspection but still benchmark-oriented |
| Zero-shot defect detection | `Zero-Shot Defect Detection With Anomaly Attribute Awareness via Textual Domain Bridge` | Adapts CLIP to anomaly attributes across 16 real-world defect datasets |
| Steel defects | `LoRA fine-tuned Qwen2.5-VL large model for accurate description and location of steel surface defects` | Fine-tunes Qwen2.5-VL for defect type and location descriptions in steel surface inspection |
| Weld inspection | `WeldLLM` | Combines YOLOv11 with Qwen2.5-VL for weld defect detection and human-readable reporting |
| Additive manufacturing | `Defect Classification and Localization in Material Extrusion with Multi-Modal Large Language Models` | GPT-4o performs well on classification but poorly on localization, exposing spatial-reasoning limits |
| Visual anomaly detection | `VMAD`, `Light-MLLMAD`, `AnomalyNLP`, `Bayes-PFL`, and CLIP-DINOv2 zero-shot AD works | Strong benchmark progress, but mostly benchmark validation rather than production quality systems |
| Root-cause reasoning | LLM + KG for cigarette quality-control causal analysis | Fine-tuned DeepSeek-R1-Distill-Llama-8B supports causal extraction over quality defects, with human validation |
| Building/crack inspection | `CracksGPT` | Fine-tuned MiniGPT-v2 classifies crack patterns and suggests causes/rectification, but expert oversight remains necessary |

## Gap Updates

- Strengthens G7/G10: industrial VLM/LLM quality inspection lacks unified benchmarks that combine detection, localization, explanation, uncertainty, traceability, operator review, and downstream quality decisions.
- Strengthens G8: systems are mostly explanation/report layers rather than validated quality-control actors that make auditable pass/fail, rework, or scrap decisions.
- Strengthens G13: corrected-label learning, active learning, drift adaptation, and self-evolving inspection loops are absent in production settings.
- Strengthens G16/G20: traceable visual evidence, image-region provenance, nonconformance audit trails, and quality-system compliance are under-specified.
- Strengthens G18/G19: real factory deployments and operator human-factors measurements are sparse.
- Adds G24: industrial LLM/VLM quality inspection lacks production-grade auditable defect-decision agents.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260428T041957Z-industrial-vlm-quality-inspection-defect-detection/openalex/manifest.json` | Full export metadata |
| `lit-watch/runs/20260428T041957Z-industrial-vlm-quality-inspection-defect-detection/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260428T041957Z-industrial-vlm-quality-inspection-defect-detection/openalex/all_results_deduped.csv` | 82 deduplicated works plus header |
| `lit-watch/runs/20260428T041957Z-industrial-vlm-quality-inspection-defect-detection/openalex/all_results_deduped.jsonl` | 82 deduplicated raw records |
| `lit-watch/runs/20260428T041957Z-industrial-vlm-quality-inspection-defect-detection/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260428T041957Z-industrial-vlm-quality-inspection-defect-detection/SUMMARY.md` | ARIS execution summary and verdict |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
