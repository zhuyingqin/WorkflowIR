# Research Wiki Index

## Papers
*(none yet)*

## Ideas
*(none yet)*

## Experiments

### OpenAlex Literature Searches

| Exp ID | Title | Date | Status | Results |
|--------|-------|------|--------|---------|
| [exp:openalex-001](experiments/exp_openalex-001.md) | OpenAlex Search — LLM Industrial Applications Survey (Initial) | 2026-04-27 | ✅ Completed | 832 deduplicated works |
| [exp:openalex-002](experiments/exp_openalex-002.md) | OpenAlex Search — LLM Industry OpenAlex Direct (Partial/Blocked) | 2026-04-27 | ⚠️ Partial | Dry-run only |
| [exp:openalex-003](experiments/exp_openalex-003.md) | OpenAlex Search — LLM Industry Trustworthy Tightening (Approved) | 2026-04-27 | ✅ Approved | 886 deduplicated works |
| [exp:openalex-004](experiments/exp_openalex-004.md) | OpenAlex Search — Industrial RLHF, PLC, SCADA, CNC Feedback Gap | 2026-04-27 | ✅ Completed | 383 deduplicated works |
| [exp:openalex-005](experiments/exp_openalex-005.md) | OpenAlex Search — LLM Digital Twin Process Control Feedback | 2026-04-27 | ✅ Completed | 347 deduplicated works |
| [exp:openalex-006](experiments/exp_openalex-006.md) | OpenAlex Search — Industrial LLM Evaluation, Safety, and Benchmarks | 2026-04-27 | ✅ Completed | 1081 deduplicated works |
| [exp:openalex-007](experiments/exp_openalex-007.md) | OpenAlex Search — Edge/SLM Industrial Deployment | 2026-04-27 | ✅ Completed with broad families | 2640 deduplicated works |
| [exp:openalex-008](experiments/exp_openalex-008.md) | OpenAlex Search — Physics/Causal/Neuro-Symbolic Industrial LLM | 2026-04-27 | ✅ Completed | 618 deduplicated works |
| [exp:openalex-009](experiments/exp_openalex-009.md) | OpenAlex Search — Self-Evolving Industrial LLM Agents | 2026-04-27 | ✅ Completed | 236 deduplicated works |
| [exp:openalex-010](experiments/exp_openalex-010.md) | OpenAlex Search — Industrial LLM OT/ICS Cybersecurity and Safety | 2026-04-27 | ✅ Completed | 55 deduplicated works |
| [exp:openalex-011](experiments/exp_openalex-011.md) | OpenAlex Search — Industrial LLM Agent Workflow Orchestration | 2026-04-27 | ✅ Completed | 300 deduplicated works |
| [exp:openalex-012](experiments/exp_openalex-012.md) | OpenAlex Search — Industrial LLM HITL Governance, Approval, and Audit | 2026-04-28 | ⚠️ Export completed; ARIS summary blocked | 305 deduplicated works |
| [exp:openalex-013](experiments/exp_openalex-013.md) | OpenAlex Search — Industrial LLM Functional Safety Assurance | 2026-04-28 | ✅ Completed | 105 deduplicated works |
| [exp:openalex-014](experiments/exp_openalex-014.md) | OpenAlex Search — Industrial LLM Field Deployment, ROI, and Production KPI Evidence | 2026-04-28 | ✅ Completed | 538 deduplicated works |
| [exp:openalex-015](experiments/exp_openalex-015.md) | OpenAlex Search — Industrial LLM Operator Human-Factors Evidence | 2026-04-28 | ✅ Completed | 516 deduplicated works |
| [exp:openalex-016](experiments/exp_openalex-016.md) | OpenAlex Search — Industrial LLM Grounded RAG, Provenance, and Traceability | 2026-04-28 | ✅ Completed | 535 deduplicated works |
| [exp:openalex-017](experiments/exp_openalex-017.md) | OpenAlex Search — Industrial LLM Sensor-Grounded PHM and Fault Diagnosis | 2026-04-28 | ✅ Completed | 157 deduplicated works |
| [exp:openalex-018](experiments/exp_openalex-018.md) | OpenAlex Search — Industrial LLM Robotics, Cobots, and Task Planning | 2026-04-28 | ✅ Completed after correction | 347 deduplicated works |
| [exp:openalex-019](experiments/exp_openalex-019.md) | OpenAlex Search — Industrial LLM Scheduling, Process Planning, and Operations Optimization | 2026-04-28 | ✅ Completed | 142 deduplicated works |
| [exp:openalex-020](experiments/exp_openalex-020.md) | OpenAlex Search — Industrial VLM/LLM Quality Inspection and Defect Detection | 2026-04-28 | ✅ Completed | 82 deduplicated works |
| [exp:openalex-021](experiments/exp_openalex-021.md) | OpenAlex Search — Typed Tool Contracts for LLM Agents | 2026-03-31 | ✅ Completed | ~409 deduplicated works |

## Claims
*(none yet)*

## Gaps

### Identified Field Gaps (from OpenAlex searches)

| Gap ID | Description | Source |
|--------|-------------|--------|
| G1 | Domain adaptation: LoRA, RLHF, fine-tuning, prompt/RAG updates, and active-learning adaptation for manufacturing/industrial domains | exp:openalex-001, exp:openalex-003, exp:openalex-009 |
| G2 | Edge LLM deployment: on-device/edge-native LLMs or SLMs for factory-floor, privacy-preserving, latency-constrained inference remain immature | exp:openalex-001, exp:openalex-003, exp:openalex-007 |
| G3 | Physics-informed, causal, and neuro-symbolic LLMs are forming a reliability cluster for industrial processes, but lack converged benchmarks, architectures, and deployment standards | exp:openalex-001, exp:openalex-003, exp:openalex-008 |
| G4 | LLM-driven digital twins: active bridge from LLM analysis to process optimization, operational decision support, and control-loop simulation | exp:openalex-001, exp:openalex-003, exp:openalex-005 |
| G5 | Manufacturing-specific agent architectures are active for factory workflows, robot workcells, HRC assembly, scheduling, process planning, maintenance, planning, and human-in-the-loop operations, but current evidence remains prototype, survey, framework, pilot, or copilot-level rather than production workflow orchestration | exp:openalex-001, exp:openalex-011, exp:openalex-014, exp:openalex-018, exp:openalex-019 |
| G6 | Explicit RLHF/RLAIF/operator-feedback/self-improvement loops for industrial LLMs are scarce, especially at PLC/SCADA/CNC/control-loop level | exp:openalex-004, exp:openalex-009 |
| G7 | Standard evaluation protocols for HITL/operator-feedback, adaptation, memory growth, OT/ICS security, workflow-agent orchestration, robot workcell action execution, planning/optimization validation, approval/audit/rollback governance, functional-safety V&V, field deployment, ROI, production-KPI measurement, human-factors validation, grounding/provenance validation, sensor/PHM validation, and constrained industrial LLMs are missing; current validation is fragmented across compiler feedback, RAG V&V, expert review, formal checks, physics consistency, causal fidelity, hallucination checks, source citation, production KPIs, safety cases, workload/trust metrics, fault-diagnosis accuracy, false alarms, time-to-detect, RUL error, task success, collision/safety violations, operator intervention, makespan, tardiness, optimality gaps, constraint violations, solver success, and ad hoc metrics | exp:openalex-004, exp:openalex-006, exp:openalex-008, exp:openalex-009, exp:openalex-010, exp:openalex-011, exp:openalex-012, exp:openalex-013, exp:openalex-014, exp:openalex-015, exp:openalex-016, exp:openalex-017, exp:openalex-018, exp:openalex-019 |
| G8 | Most industrial LLM papers use LLMs as analysts or decision-support layers rather than as validated controllers, autonomous remediation agents, governed workflow orchestrators, autonomous optimization actors, sensor-grounded diagnostic/PHM actors, safe robot workcell actors, or safety-certified operational actors that generate or adjust operational actions with measured operator behavior, grounded evidence, and production KPI evidence | exp:openalex-004, exp:openalex-005, exp:openalex-006, exp:openalex-010, exp:openalex-011, exp:openalex-012, exp:openalex-013, exp:openalex-014, exp:openalex-015, exp:openalex-016, exp:openalex-017, exp:openalex-018, exp:openalex-019 |
| G9 | Digital-twin-mediated safety validation and simulation-to-operation feedback for industrial LLM control lack standardized closed-loop benchmarks and operator-feedback protocols | exp:openalex-005, exp:openalex-006 |
| G10 | Cross-domain industrial LLM benchmark suites are missing; existing benchmarks are fragmented across PLC code, industrial RAG, source citation/faithfulness, UAV cybersecurity, OT/ICS security, HITL fault diagnosis, sensor/PHM fault diagnosis, RUL, multimodal inspection, process anomaly monitoring, robot programming, HRC assembly, workcell task execution, production scheduling, process planning, solver-backed optimization, digital-twin validation, edge deployment, self-improvement, workflow orchestration, functional safety, production deployment maturity, ROI/KPI reporting, operator human-factors metrics, and physics/causal/symbolic reliability checks | exp:openalex-006, exp:openalex-007, exp:openalex-008, exp:openalex-009, exp:openalex-010, exp:openalex-011, exp:openalex-013, exp:openalex-014, exp:openalex-015, exp:openalex-016, exp:openalex-017, exp:openalex-018, exp:openalex-019 |
| G11 | Production-grade, safety-certified edge-native or on-prem LLM/SLM controllers and security copilots for industrial systems are absent; current systems remain cloud-predominant with edge augmentation and lack functional-safety certification pathways | exp:openalex-007, exp:openalex-010, exp:openalex-013 |
| G12 | Physics/causal/neuro-symbolic constraints for industrial LLMs are recognized as necessary reliability layers but are not yet standardized, real-time capable, safety-certified, or production-ready | exp:openalex-008 |
| G13 | True self-evolving industrial LLMs are absent; current self-improvement is mostly external, batch-style, human-supervised, and implemented through feedback pipelines, memory stores, active learning, digital twins, static skill libraries, or population-level heuristic evolution rather than autonomous LLM weight updates; safe update approval, audit trails, rollback, safety-case updates, recertification, operator-feedback burden, sensor/PHM drift adaptation, robot skill-library growth, and schedule-repair memory remain unresolved | exp:openalex-009, exp:openalex-012, exp:openalex-013, exp:openalex-015, exp:openalex-017, exp:openalex-018, exp:openalex-019 |
| G14 | OT/ICS LLM security copilots lack production validation, OT-specific benchmarks, and safe remediation protocols; current evidence is sparse and mostly analyst-support or code-analysis oriented | exp:openalex-010 |
| G15 | MES/ERP/CMMS/APS/work-order LLM orchestration is essentially unexplored; current industrial LLM agents do not autonomously create, route, schedule, optimize, execute, approve, audit, or close operational work orders with measured production KPI impact or grounded plant-data provenance | exp:openalex-011, exp:openalex-012, exp:openalex-014, exp:openalex-016, exp:openalex-019 |
| G16 | Industrial LLM governance for operator approval, auditability, traceability, rollback, change management, safety cases, fail-safe fallback, source attribution, constraint provenance, and approval-burden measurement is under-specified, especially for self-improving LLMs, workflow agents, and optimization/planning agents | exp:openalex-012, exp:openalex-013, exp:openalex-015, exp:openalex-016, exp:openalex-019 |
| G17 | Safety-certified autonomous industrial LLM agents lack functional-safety assurance cases, formal verification, runtime monitoring, fail-safe fallback, IEC 61508/ISO 13849 certification pathways, and ISO 10218/ISO/TS 15066 evidence for robot workcells | exp:openalex-013, exp:openalex-018 |
| G18 | Real production deployment, ROI, payback, MTBF, maintenance-cost savings, scrap-rate reduction, incident-resolution time, operator-level value, grounded plant-data evidence, sensor/PHM operational evidence, robot workcell production evidence, scheduling/optimization production evidence, and production-KPI evidence for industrial LLM systems is sparse despite a large surface-level literature | exp:openalex-014, exp:openalex-015, exp:openalex-016, exp:openalex-017, exp:openalex-018, exp:openalex-019 |
| G19 | HITL/operator human-factors validation for industrial LLM systems is missing; NASA-TLX, SUS, trust calibration, reliance/overreliance, override rate, approval latency, HRC intervention behavior, and longitudinal operator behavior are rarely measured | exp:openalex-015, exp:openalex-018 |
| G20 | Validated industrial LLM grounding/provenance mechanisms for plant data are missing; RAG/KG/digital-twin grounding is mostly prototype-level, while MES/SCADA/PLC/CMMS source attribution, data lineage, citation faithfulness, and provenance completeness are rarely measured | exp:openalex-016 |
| G21 | Sensor-grounded industrial LLM diagnostics and PHM remain immature; direct sensor/time-series/multimodal data to LLM fault diagnosis is rare, mostly lab-benchmark based, and often conventional PHM plus LLM explanation rather than production-validated maintenance decision systems | exp:openalex-017 |
| G22 | Industrial LLM robotics and cobot systems lack production-certified safe workcell execution; current evidence is mostly language interfaces, ROS/ROS2 or digital-twin prototypes, lab robots, simulation, field trials, and HRC pilots rather than ISO-certified autonomous production agents | exp:openalex-018 |
| G23 | LLM-enabled industrial planning and optimization lacks production-grade autonomous constrained optimization; current systems mainly generate formulations, constraints, heuristics, process chains, or explanations while external solvers and human planners remain responsible for feasibility, safety, and deployment decisions | exp:openalex-019 |
| G24 | Industrial LLM/VLM quality inspection lacks production-grade auditable defect-decision agents; current systems mostly add report generation, explanations, prompts, or semantic alignment over conventional vision backbones, with weak localization, little deployment, and no drift-adaptive corrected-label feedback loop | exp:openalex-020 |

## Last Updated
2026-04-28T04:26:26Z (auto-updated from lit-watch run `20260428T041957Z-industrial-vlm-quality-inspection-defect-detection`)
