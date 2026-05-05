# Research Wiki Log

## Timeline

| Date | Event |
|------|-------|
| 2026-03-31T00:00:00Z | Wiki initialized |
| 2026-04-27T08:00:00Z | Ingested 3 OpenAlex literature search runs (lit-watch/runs/) |
| 2026-04-27T08:00:00Z | Created experiment records: exp:openalex-001, exp:openalex-002, exp:openalex-003 |
| 2026-04-27T08:00:00Z | Identified 5 field gaps (G1-G5) from OpenAlex search results |
| 2026-04-27T08:00:00Z | Updated index.md with experiment summary and gap map |
| 2026-04-27T16:25:00Z | Ingested OpenAlex run `20260427T161817Z-industrial-rlhf-plc-scada-feedback` as exp:openalex-004 |
| 2026-04-27T16:25:00Z | Confirmed gap G6: explicit RLHF/RLAIF/operator-feedback industrial LLMs are scarce at PLC/SCADA/CNC/control-loop level |
| 2026-04-27T16:25:00Z | Updated gap map with G6-G8 and refreshed index.md with 383 deduplicated works |
| 2026-04-27T16:52:42Z | Ingested OpenAlex run `20260427T164456Z-llm-digital-twin-process-control-feedback` as exp:openalex-005 |
| 2026-04-27T16:52:42Z | Strengthened G4: LLM-enabled digital twins are an active bridge candidate from analysis to operational decision support and control-loop simulation |
| 2026-04-27T16:52:42Z | Added G9: digital-twin-mediated safety validation and simulation-to-operation feedback for industrial LLM control lack standardized closed-loop benchmarks |
| 2026-04-27T17:30:00Z | Ingested OpenAlex run `20260427T171326Z-industrial-llm-evaluation-safety-benchmarks` as exp:openalex-006 |
| 2026-04-27T17:30:00Z | Confirmed that industrial LLM evaluation and safety remain the central bottleneck despite emerging task-specific benchmarks |
| 2026-04-27T17:30:00Z | Added G10: cross-domain industrial LLM benchmark suites are missing across PLC code, industrial RAG, HITL feedback, and digital-twin validation |
| 2026-04-27T17:55:00Z | Ingested OpenAlex run `20260427T174756Z-edge-slm-industrial-deployment` as exp:openalex-007 |
| 2026-04-27T17:55:00Z | Confirmed G2 as an open gap: industrial LLM deployment is cloud-predominant with edge augmentation rather than edge-native local inference |
| 2026-04-27T17:55:00Z | Added G11: production-grade, safety-certified edge-native LLM/SLM controllers for industrial systems are absent |
| 2026-04-27T20:42:08Z | Ingested OpenAlex run `20260427T203256Z-physics-causal-neurosymbolic-industrial-llm` as exp:openalex-008 |
| 2026-04-27T20:42:08Z | Updated G3: physics-informed, causal, and neuro-symbolic industrial LLMs are forming but fragmented rather than mature |
| 2026-04-27T20:42:08Z | Added G12: physics/causal/neuro-symbolic reliability layers are necessary for industrial LLM safety but are not standardized or production-ready |
| 2026-04-27T21:05:41Z | Ingested OpenAlex run `20260427T205926Z-self-evolving-industrial-llm-agents` as exp:openalex-009 |
| 2026-04-27T21:05:41Z | Strengthened G6: focused operator-feedback search returned only 1 work, reinforcing scarcity of explicit industrial LLM feedback loops |
| 2026-04-27T21:05:41Z | Added G13: true self-evolving industrial LLMs are absent; current self-improvement is mostly external, batch-style, human-supervised, and pipeline-mediated |
| 2026-04-27T21:27:58Z | Ingested OpenAlex run `20260427T212257Z-industrial-llm-ot-ics-cybersecurity-safety` as exp:openalex-010 |
| 2026-04-27T21:27:58Z | Strengthened G7/G10: OT/ICS LLM security evaluation remains sparse, with no dedicated benchmark for hallucination, adversarial robustness, or physical-process impact |
| 2026-04-27T21:27:58Z | Added G14: OT/ICS LLM security copilots lack production validation, OT-specific benchmarks, and safe remediation protocols |
| 2026-04-27T21:52:14Z | Ingested OpenAlex run `20260427T214457Z-industrial-llm-agent-workflow-orchestration` as exp:openalex-011 |
| 2026-04-27T21:52:14Z | Updated G5: manufacturing-specific LLM agents are active but still immature as production workflow orchestrators |
| 2026-04-27T21:52:14Z | Added G15: MES/ERP/CMMS/work-order LLM orchestration is essentially unexplored and lacks concrete autonomous agent integration |
| 2026-04-28T00:42:19Z | Ingested OpenAlex run `20260427T222217Z-industrial-llm-hitl-governance-approval-audit` as exp:openalex-012 |
| 2026-04-28T00:42:19Z | Recorded blocker: ARIS completed OpenAlex export but hit context-window overflow before writing SUMMARY.md; Codex recovered summary from exported metadata |
| 2026-04-28T00:42:19Z | Added G16: industrial LLM governance for approval, auditability, rollback, and change management is under-specified |
| 2026-04-28T01:06:58Z | Ingested OpenAlex run `20260428T010226Z-industrial-llm-functional-safety-assurance` as exp:openalex-013 |
| 2026-04-28T01:06:58Z | Confirmed functional safety as a blocker: only two concrete ISO 12100/ISO 13849 LLM safety-risk-assessment papers, no SIL-rated LLM controller evidence |
| 2026-04-28T01:06:58Z | Added G17: safety-certified autonomous industrial LLM agents lack assurance cases, formal verification, runtime monitors, fail-safe fallback, and IEC 61508/ISO 13849 certification pathways |
| 2026-04-28T01:37:00Z | Ingested OpenAlex run `20260428T012856Z-industrial-llm-field-deployment-roi-kpi` as exp:openalex-014 |
| 2026-04-28T01:37:00Z | Confirmed that industrial LLM field-deployment evidence remains sparse: 538 deduplicated works produced only a few credible production-adjacent metric papers |
| 2026-04-28T01:37:00Z | Added G18: real production deployment, ROI, payback, MTBF, maintenance-cost savings, and production-KPI evidence for industrial LLM systems is sparse |
| 2026-04-28T02:04:00Z | Ingested OpenAlex run `20260428T015556Z-industrial-llm-operator-human-factors` as exp:openalex-015 |
| 2026-04-28T02:04:00Z | Confirmed that industrial LLM HITL remains mostly assumed rather than empirically validated: 516 deduplicated works contained few operator human-factors measurements |
| 2026-04-28T02:04:00Z | Added G19: HITL/operator human-factors validation for industrial LLMs lacks NASA-TLX, SUS, trust calibration, override rate, approval latency, and longitudinal reliance evidence |
| 2026-04-28T02:32:00Z | Ingested OpenAlex run `20260428T022326Z-industrial-llm-grounded-rag-provenance` as exp:openalex-016 |
| 2026-04-28T02:32:00Z | Confirmed that industrial LLM grounding/provenance is mostly prototype-level: 535 deduplicated works included few validated plant-data provenance mechanisms |
| 2026-04-28T02:32:00Z | Added G20: validated industrial LLM grounding/provenance for MES/SCADA/PLC/CMMS plant data is missing, with source attribution and provenance metrics rarely measured |
| 2026-04-28T03:01:14Z | Ingested OpenAlex run `20260428T025126Z-industrial-llm-sensor-phm-fault-diagnosis` as exp:openalex-017 |
| 2026-04-28T03:01:14Z | Confirmed that sensor-grounded industrial LLM fault diagnosis and PHM remain mostly lab-benchmark or explanation-layer systems: 157 deduplicated works produced few direct sensor-to-LLM diagnostic systems and no production deployments |
| 2026-04-28T03:01:14Z | Added G21: sensor-grounded industrial LLM diagnostics and PHM lack production validation, active drift adaptation, operator-correction loops, and standardized sensor/PHM benchmarks |
| 2026-04-28T03:32:28Z | Ingested OpenAlex run `20260428T031956Z-industrial-llm-robotics-cobot-task-planning` as exp:openalex-018 |
| 2026-04-28T03:32:28Z | Recorded correction: initial cobot/HRC query reported 569 works and was rejected; corrected query produced 72 works and a compliant 347-work deduplicated export |
| 2026-04-28T03:32:28Z | Added G22: industrial LLM robotics and cobot systems lack production-certified safe workcell execution despite lab, simulation, field-trial, and HRC pilot evidence |
| 2026-04-28T03:59:53Z | Ingested OpenAlex run `20260428T035157Z-industrial-llm-scheduling-process-planning-optimization` as exp:openalex-019 |
| 2026-04-28T03:59:53Z | Confirmed that industrial LLM planning/optimization is mostly formulation generation, solver orchestration, and natural-language decision support: 142 deduplicated works produced few production deployments and no autonomous LLM optimizer evidence |
| 2026-04-28T03:59:53Z | Added G23: LLM-enabled industrial planning and optimization lacks production-grade autonomous constrained optimization; external solvers and human planners remain responsible for feasibility, safety, and deployment decisions |
| 2026-04-28T04:26:26Z | Ingested OpenAlex run `20260428T041957Z-industrial-vlm-quality-inspection-defect-detection` as exp:openalex-020 |
| 2026-04-28T04:26:26Z | Confirmed that industrial VLM/LLM quality inspection is mostly report generation, explanation, prompt generation, and semantic alignment over conventional visual backbones: 82 deduplicated works produced little production deployment evidence and no self-evolving inspection loop |
| 2026-04-28T04:26:26Z | Added G24: industrial LLM/VLM quality inspection lacks production-grade auditable defect-decision agents with traceability, operator feedback, drift adaptation, and quality-system compliance |
| 2026-03-31T01:26:00Z | Ingested OpenAlex run `20260505T012607Z-typed-tool-contracts-for-llm-agents` as exp:openalex-021 |
| 2026-03-31T01:26:00Z | Confirmed that formal typed tool contracts for LLM agents is an open gap: no papers found addressing preconditions/effects/workflow IR; field uses "tool use" / "function calling" terminology |
| 2026-03-31T01:26:00Z | Added G25: formal verification and type-theoretic foundations for LLM tool contracts — specifically schema validation frameworks, precondition/effect modeling, static validation pipelines, and contract-aware failure prevention — are absent from the literature |
