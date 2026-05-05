---
type: experiment
node_id: exp:openalex-010
title: "OpenAlex Search - Industrial LLM OT/ICS Cybersecurity and Safety"
run_id: "20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety"
date: 2026-04-27T21:27:58Z
skill: openalex-search
status: completed
verdict: experimental_ot_security_copilots_not_production_ready
freshness_window: "2024-04-27 to 2026-04-27"
---

# OpenAlex Search - Industrial LLM OT/ICS Cybersecurity and Safety

**Run ID**: `20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety`
**Status**: Completed
**Verdict**: LLMs are emerging as experimental OT security analysts and PLC-code security helpers, but not as production-ready OT security copilots or autonomous remediation agents.

## Purpose

This run tested whether LLMs solve concrete OT/ICS cybersecurity problems in SCADA, PLC, DCS, IIoT, industrial control systems, and safety-critical cyber-physical environments. It focused on LLM-as-analyst workflows, PLC/control-code security, RAG/KG grounding, incident response, evaluation, hallucination mitigation, and safety/reliability constraints.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-27 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran dry-run first; all families were already under 300, so full export proceeded without additional tightening.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `llm_ics_scada_cybersecurity` | 19 | 19 | 1 |
| `llm_plc_code_security_verification` | 10 | 10 | 1 |
| `llm_ot_incident_response_playbooks` | 4 | 4 | 1 |
| `industrial_rag_llm_security_grounding` | 4 | 4 | 1 |
| `llm_ics_security_evaluation_benchmarks` | 20 | 20 | 1 |

**Total downloaded rows**: 57
**Total deduplicated works**: 55

## Quality Notes

The corpus is small but high-signal. One off-topic education paper matched the evaluation query and should be ignored. The remaining works show a nascent but scattered field: LLMs appear in device fingerprinting, PLC code vulnerability detection, SOC/RAG copilots, critical-infrastructure protection reviews, and LLM security evaluation, but the OT-specific evidence remains thin.

## Key Findings

1. No production OT security copilot was found for live SCADA/PLC/DCS environments.
2. PLC code security is the most concrete LLM contribution: fine-tuned CodeLlama/Qwen2.5-Coder/StarCoder2 models are evaluated on IEC 61131-3 Structured Text vulnerability detection, but datasets remain synthetic or limited.
3. ICS anomaly detection has one explicit Llama3 fine-tuning example for oilfield device fingerprinting, but much of the wider anomaly detection literature is conventional supervised ML/DL rather than LLM agents.
4. RAG-based SOC copilots such as Wazuh/SERC and RAGIntel show promising grounded analyst workflows, but are validated mainly in IT/SOC contexts rather than industrial OT networks.
5. Incident-response papers for cyber-physical systems use security-enhancing digital twins and playbook concepts, but not OT-specific LLM response generation.
6. No OT/ICS-specific LLM benchmark suite was found for PLC code security, SCADA incident response, hallucination rate, adversarial robustness, or physical process safety impact.
7. Autonomous LLM remediation in ICS remains unsafe and undocumented; all credible workflows require human analyst approval before action.

## Representative Papers

| Mechanism | Representative Paper |
|---|---|
| ICS anomaly detection with LLM | `An Anomaly Detection Method for Oilfield Industrial Control Systems Fine-Tuned Using the Llama3 Model` |
| ICS security survey | `Artificial intelligence for secure and sustainable industrial control systems - A Survey of challenges and solutions` |
| PLC code vulnerability detection | `Fine-Tune LLMs for PLC Code Security: An Information-Theoretic Analysis` |
| PLC fuzzing baseline | `ICS-QUARTZ: Scan Cycle-Aware and Vendor-Agnostic Fuzzing for Industrial Control Systems` |
| Safety-security convergence | `Safety-security convergence: Automation of IEC 62443-3-2` |
| CPS incident response | `A framework for enhancing cyber incident response with Security-Enhancing Digital Twins in CPS` |
| SOC/RAG copilot | `Enhancing Security Operations Center: Wazuh Security Event Response with RAG-Driven Copilot` |
| RAG threat intelligence | `LLM-powered threat intelligence: a RAG approach for cyber attack investigation` |
| Critical infrastructure LLM benchmarks | `Generative AI and LLMs for Critical Infrastructure Protection: Evaluation Benchmarks, Agentic AI, Challenges` |
| Security strategy benchmark | `MACD: Multi-Agent Collaborative Approach for Cybersecurity Defense Strategy Generation` |

## Gap Updates

- Strengthens G7/G10: OT/ICS LLM security lacks standardized evaluation for hallucination, adversarial robustness, physical-process impact, and safe response quality.
- Strengthens G8: no LLM-as-controller or autonomous remediation evidence exists for ICS; LLMs remain analyst-support layers.
- Strengthens G11: OT security deployment faces air-gapped, edge/on-prem, low-latency, and safety-certification constraints.
- Adds G14: OT/ICS LLM security copilots lack production validation, OT-specific benchmarks, and safe remediation protocols.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety/openalex/manifest.json` | Full run metadata and API params |
| `lit-watch/runs/20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety/openalex/query_counts.csv` | Per-query reported/downloaded counts |
| `lit-watch/runs/20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety/openalex/all_results_deduped.csv` | 55 deduplicated works plus header |
| `lit-watch/runs/20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety/openalex/all_results_deduped.jsonl` | 55 deduplicated raw records |
| `lit-watch/runs/20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety/openalex_queries.json` | Reproducible query plan |
| `lit-watch/runs/20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety/SUMMARY.md` | Run summary and survey implications |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
