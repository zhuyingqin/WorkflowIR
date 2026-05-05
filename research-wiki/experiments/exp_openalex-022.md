# OpenAlex Search — LLM Agent Error Recovery and Failure Attribution in Multi-Tool Workflows

## Experiment Metadata

| Field | Value |
|-------|-------|
| **Exp ID** | exp:openalex-022 |
| **Date** | 2026-03-31 |
| **Topic** | LLM agent error recovery and failure attribution in multi-tool workflows, including tool failure localization, counterexample-guided repair, retry policies, and trace diagnostics |
| **Status** | ✅ Completed |
| **Results** | 346 deduplicated works |

## Reviewer Direction

**Priority direction**: Fault Localization and Failure Attribution Taxonomy in LLM Multi-Tool Agents

**Why it matters**:
- Debugging: Multi-tool agent failures are black boxes; attribution turns failures into actionable signals
- Trust & Calibration: Users need to know whether to trust an agent's output given a tool failure
- Safety & Compliance: Attribution supports post-hoc explainability and accountability
- Autonomous Agent Reliability: Without attribution, agents cannot selectively retry or switch strategies

**What to avoid**: Industrial/manufacturing themes (PLC/SCADA, digital twins, edge deployment, robotics in factory settings), functional safety (IEC 61508, ISO 26262), sensor/PHM, quality inspection.

**Query families**: 6 query families targeting fault localization, error attribution, self-correction, counterfactual repair, fault diagnosis, and debugging in LLM agents.

**Stop criteria**: Landmark papers found (3-5 high-citation papers), query family saturation (>50% overlap), max 200-300 unique papers per family, practical ceiling of 5 search rounds.

## Query Families

| Name | Final Formula | Dry-Run Count | Downloaded |
|------|--------------|---------------|------------|
| fault_localization_llm_agents | `"fault localization" AND (LLM OR "large language model")` | 250 | 150 (capped) |
| error_attribution_llm_agent | `"error attribution" OR "failure attribution" AND (LLM OR agent OR tool OR workflow)` | 97 | 97 |
| self_correction_llm_tool_use | `"self-correct" OR "self-repair" OR retry` + title_and_abstract filter | 11 | 11 |
| counterfactual_llm_agent_repair | `counterfactual AND (LLM OR agent)` + title_and_abstract filter | 3 | 3 |
| llm_agent_fault_diagnosis | `"fault diagnosis" OR "root cause" AND (LLM OR agent OR tool)` + title_and_abstract filter | 66 | 66 |
| llm_debugging_tool_workflow | `LLM AND debugging AND (tool OR workflow)` + title_and_abstract filter | 19 | 19 |

## Query Revisions

- **Round 1**: 4 of 5 initial queries returned 0 — overly restrictive AND chains
- **Round 2**: Simplified queries; still self_correction=0 and tool_use_debugging=7592
- **Round 3**: All 6 queries return non-zero; tool_use_debugging tightened; self_correction simplified

## Top Core Papers

1. **"A Quantitative and Qualitative Evaluation of LLM-Based Explainable Fault Localization"** — DOI: 10.1145/3660771, ACM FSE 2024, 68 citations. Function-call navigation for LLM-based fault localization; 798 real-world bugs; human evaluation.

2. **"AutoCodeRover: Autonomous Program Improvement"** — DOI: 10.1145/3650212.3680384, ACM FSE 2024, 87 citations. LLM agent combines code search with spectrum-based fault localization; SWE-bench-lite evaluation.

3. **"SoapFL: A Standard Operating Procedure for LLM-Based Method-Level Fault Localization"** — DOI: 10.1109/tse.2025.3543187, IEEE TSE 2025. SOP-style debugging; multi-round dialogue; Defects4J evaluation.

4. **"Counterexample Guided Program Repair Using Zero-Shot Learning and MaxSAT-based Fault Localization"** — DOI: 10.1609/aaai.v39i1.32046, AAAI 2025. CEGIS loop for LLM-based program repair; counterexample feedback to LLM.

5. **"ContrastRepair: Enhancing Conversation-Based Automated Program Repair via Contrastive Test Case Pairs"** — DOI: 10.1145/3719345, ACM TOSEM 2025, 17 citations. Contrastive test pairs as feedback to LLMs; 143/337 bugs repaired.

6. **"Building AI Agents for Autonomous Clouds: Challenges and Design Principles"** — DOI: 10.1145/3698038.3698525, ACM SIGSOFT 2024, 16 citations. AIOpsLab for agent evaluation; fault localization and root cause analysis for autonomous cloud agents.

## Confirmed Gaps

- **G26**: Formal typed tool contracts and precondition/effect modeling for LLM agents — no papers found
- **G27**: Explicit failure attribution taxonomies in multi-tool LLM agents — current literature uses "fault localization" but doesn't systematically attribute failures to agent vs. tool vs. downstream service
- **G28**: Retry policy frameworks for LLM tool-use — self-correction papers are mostly post-hoc repair rather than runtime retry strategies
- **G29**: Multi-agent coordination failure attribution — most current work focuses on single-agent fault localization; multi-agent coordination failure attribution is absent

## Suggested Next Searches

- `exp:openalex-023`: LLM agent recovery and graceful degradation in multi-tool workflows
- `exp:openalex-024`: Typed tool contracts and schema validation for LLM agents
- `exp:openalex-025`: Multi-agent coordination failure attribution

## Export Location

`/Users/zhuyingqin/Documents/New project/Auto-claude-code-research-in-sleep/lit-watch/real-agent-trials/20260505T013422Z-llm-agent-error-recovery-and-failure-attribution-in-multi-tool-workflows-includi/openalex/`