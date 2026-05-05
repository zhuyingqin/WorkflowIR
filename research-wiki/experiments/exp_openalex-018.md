---
type: experiment
node_id: exp:openalex-018
title: "OpenAlex Search - Industrial LLM Robotics, Cobots, and Task Planning"
run_id: "20260428T031956Z-industrial-llm-robotics-cobot-task-planning"
date: 2026-04-28T03:32:28Z
skill: openalex-search
status: completed
verdict: industrial_llm_robotics_lab_and_field_trial_not_production_certified
freshness_window: "2024-04-27 to 2026-04-28"
---

# OpenAlex Search - Industrial LLM Robotics, Cobots, and Task Planning

**Run ID**: `20260428T031956Z-industrial-llm-robotics-cobot-task-planning`
**Status**: Completed after correction
**Verdict**: Industrial LLM robotics is moving from language interfaces and lab prototypes toward field trials, but safe, certified, autonomous LLM-driven robot workcell execution is not yet production validated.

## Purpose

This run tested whether LLMs are becoming validated operational agents for industrial robot programming, task planning, assembly, inspection, workcell orchestration, and safe human-robot collaboration, or whether they remain language interfaces, simulation demos, and lab prototypes.

## Query Plan Summary

The run used a 2024-04-27 to 2026-04-28 freshness window with `type:article`, `language:en`, `is_retracted:false`, and `is_paratext:false`. ARIS ran dry-runs first, tightened over-broad query families, then corrected one non-compliant export where the cobot/HRC query initially reported 569 works. The corrected final export keeps every query at or below 300 reported works.

| Query Family | Reported | Downloaded | Pages |
|---|---:|---:|---:|
| `industrial_llm_robot_task_planning` | 76 | 76 | 1 |
| `llm_cobot_human_robot_collaboration_assembly` | 72 | 72 | 1 |
| `llm_robot_programming_manufacturing_natural_language` | 39 | 39 | 1 |
| `llm_robot_manipulation_factory_assembly` | 243 | 243 | 2 |
| `llm_industrial_robot_safety_hitl` | 48 | 48 | 1 |

**Total downloaded rows**: 478
**Total deduplicated works**: 347

## Query Tightening Notes

- Initial dry-run counts were 1400, 569, 1591, 243, and 1064 works.
- `industrial_llm_robot_task_planning`, `llm_robot_programming_manufacturing_natural_language`, and `llm_industrial_robot_safety_hitl` were tightened with single `title_and_abstract.search` filters.
- A first export left `llm_cobot_human_robot_collaboration_assembly` at 569 works and was rejected as non-compliant.
- Correction narrowed that family to `"large language model" collaborative robot assembly` plus `title_and_abstract.search:collaborative robot`, yielding 72 works.

## Key Findings

1. LLMs are genuinely useful as high-level task planners, natural-language programming interfaces, code generators, VLM-grounded perception-action helpers, and operator-facing HRC interfaces.
2. The strongest field-trial or pilot signals include RoboSpection for real industrial visual inspection, AR-assisted HRC assembly, LLM-driven dynamic trajectory planning, fine-tuned LLM + digital twin reducer assembly, and dual-agent validated vocal HRC.
3. Most systems remain lab robot, simulation, benchmark, prototype, or review/conceptual work rather than production workcell deployment.
4. ROS/ROS2 is the dominant integration layer; digital twins often provide simulation-to-real context; local/offline LLM deployment is emerging for privacy-sensitive industrial settings.
5. Safety is mostly handled by keeping humans, ROS, and low-level controllers in the loop. LLMs generate plans or code, but do not own safety-critical control.
6. No paper reports ISO 10218 or ISO/TS 15066 certification for an LLM-driven robot workcell.
7. Self-evolution is weak: human override, dynamic knowledge bases, online replanning, and fine-tuning appear, but no lifelong skill-library growth, operator-preference learning loop, or autonomous safe adaptation was found.

## Representative Papers

| Problem Class | Representative Paper | Takeaway |
|---|---|---|
| Robot task planning | `A vision-language-guided robotic action planning approach for ambiguity mitigation in HRC manufacturing` | Strong HRC manufacturing signal with real cobot setup and ambiguity mitigation |
| Multi-agent HRC planning | `LLM-based multi-agent task planning for HRC collaborative assembly balancing operator experience and efficiency` | LLMs coordinate assembly planning with operator-experience tradeoffs |
| Dynamic trajectory planning | `LLM-driven dynamic trajectory planning for human-guided robot assembly` | LLM/VLM generates task-level trajectory support, but validation is still industrial-scenario or lab level |
| Cobot/HRC assembly | `Enhancing Human-Robot Collaborative Assembly in Manufacturing Using LLMs` | Voice/NL task management for real HRC assembly |
| Offline inspection robot | `Human-robot collaborative visual inspection with Large Language Models` | RoboSpection combines offline LLM, speech, ROS low-level control, and real industrial inspection |
| NL robot programming | `Embodied AI Agent Framework for (Re)Programming Robotic Tasks in Flexible Assembly using LLMs and VLMs` | ROS2-based NL-to-action framework with real cable manipulation |
| Robot safety/HITL | `Transforming Robots into Cobots: A Sustainable Approach to Industrial Automation` | ISO/TS 15066-aware retrofit framework, but mostly conceptual/theoretical |

## Gap Updates

- Strengthens G5: manufacturing agents now include robot workcell and HRC planners, but remain mostly prototype/pilot rather than production orchestrators.
- Strengthens G7: action-level robotics evaluation needs task success, collision/safety violations, operator intervention, latency, cycle-time, and simulation-to-real metrics.
- Strengthens G8: LLMs are not validated safety-certified robot operational actors; they remain high-level planners/interfaces supervised by ROS, low-level controllers, and humans.
- Strengthens G10: cross-domain industrial LLM benchmarks do not cover robot programming, HRC assembly, workcell task execution, safety violations, or simulation-to-real transfer.
- Strengthens G13: robot skill-library growth, lifelong learning, operator-preference learning, and safe adaptation are absent.
- Strengthens G17: LLM-driven robot workcells lack ISO 10218 or ISO/TS 15066 certification evidence.
- Strengthens G18: production workcell deployment and KPI evidence remain absent despite field-trial signals.
- Strengthens G19: some HRC papers report workload/intervention metrics, but longitudinal operator behavior and approval burden remain sparse.
- Adds G22: industrial LLM robotics and cobot systems lack production-certified safe workcell execution.

## Output Files

| File | Description |
|---|---|
| `lit-watch/runs/20260428T031956Z-industrial-llm-robotics-cobot-task-planning/openalex/manifest.json` | Corrected full export metadata |
| `lit-watch/runs/20260428T031956Z-industrial-llm-robotics-cobot-task-planning/openalex/query_counts.csv` | Corrected per-query reported/downloaded counts |
| `lit-watch/runs/20260428T031956Z-industrial-llm-robotics-cobot-task-planning/openalex/all_results_deduped.csv` | 347 deduplicated works plus header |
| `lit-watch/runs/20260428T031956Z-industrial-llm-robotics-cobot-task-planning/openalex/all_results_deduped.jsonl` | 347 deduplicated raw records |
| `lit-watch/runs/20260428T031956Z-industrial-llm-robotics-cobot-task-planning/openalex_queries.json` | Corrected reproducible query plan |
| `lit-watch/runs/20260428T031956Z-industrial-llm-robotics-cobot-task-planning/SUMMARY.md` | Corrected ARIS execution summary and verdict |

## Connections

[AUTO-GENERATED from graph/edges.jsonl - do not edit manually]
