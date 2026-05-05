# Real Agent Lit-Watch Trace Dataset v1

Dataset id: `real_agent_litwatch_traces_v1`

This dataset is mined from existing ARIS/Codex literature-watch run artifacts.
Unlike the controlled synthetic sandbox, these rows come from actual agent
workflow outputs: prompts, reviewer directions, OpenAlex query plans, OpenAlex
export manifests, summaries, blocked records, stdout, and stderr when present.

## Scope

- Runs: 23
- Events: 235
- Automatically detected anomalies: 25

## Files

- `run_traces.jsonl`: one row per real lit-watch run.
- `tool_events.jsonl`: artifact-level event stream and OpenAlex query events.
- `anomalies.jsonl`: weak anomaly labels mined from artifacts.
- `manifest.json`: counts and dataset notes.
- `schema.json`: compact schema summary.

## Important Caveat

This is a real artifact-level trace dataset, not yet a full per-token/per-tool
agent telemetry dataset. To capture exact LLM tool-call arguments, retries, and
exceptions, the next step is to instrument the ARIS/Codex tool runtime and write
JSONL events during live agent execution.
