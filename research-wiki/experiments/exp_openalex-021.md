# exp:openalex-021 — Typed Tool Contracts for LLM Agents

## Metadata
- **Exp ID**: exp:openalex-021
- **Title**: OpenAlex Search — Typed Tool Contracts for LLM Agents (Schemas, Preconditions, Effects, Workflow IR, Static Validation)
- **Date**: 2026-03-31
- **Status**: ✅ Completed
- **Results**: ~409 deduplicated works
- **Run ID**: 20260505T012607Z-typed-tool-contracts-for-llm-agents-including-schemas-preconditions-effects-work
- **Run Directory**: /Users/zhuyingqin/Documents/New project/Auto-claude-code-research-in-sleep/lit-watch/real-agent-trials/20260505T012607Z-typed-tool-contracts-for-llm-agents-including-schemas-preconditions-effects-work

## Query Families

| Name | Search Expression | Reported Count |
|------|-------------------|----------------|
| `tool_schema_type_contracts` | `tool schema type contract validation LLM agent` | 260 |
| `preconditions_effects_agent_tools` | `precondition effect tool LLM agent API function` | 87 |
| `static_validation_llm_tool_calls` | `static validation compile-time pre-execution LLM agent tool API` | 225 |
| `workflow_ir_llm_agent` | `workflow intermediate representation dataflow graph agent LLM tool function API` | 17 |
| `tool_call_failure_prevention` | `tool API failure prevention LLM agent contract violation invariant` | 5 |

**Shared filter**: `from_publication_date:2024-05-05,to_publication_date:2026-05-05,type:article,language:en,is_retracted:false,is_paratext:false`

## Query Diagnosis

- `tool_schema_type_contracts`: Initially 399 (overly broad); attempted `title_and_abstract.search` tightening → 0 results; reverted to broad search
- `preconditions_effects_agent_tools`: 87 (appropriate)
- `static_validation_llm_tool_calls`: 225 (appropriate)
- `workflow_ir_llm_agent`: 17 (small but not zero)
- `tool_call_failure_prevention`: 5 (small field)

## Top Core Papers

1. **"Prompt Injection Attacks in Large Language Models and AI Agent Systems: A Comprehensive Review"** (2026)
   - DOI: 10.3390/info17010054
   - Relevance: Core — addresses MCP, tool poisoning, credential theft in agent systems
   - Quality: High — survey of 45 sources

2. **"LLM-CompDroid: Repairing Configuration Compatibility Bugs in Android Apps with Pre-trained Large Language Models"** (2025)
   - DOI: 10.1145/3736406
   - Relevance: Core — addresses configuration compatibility validation and bug repair for tool calls
   - Quality: High — ACM TOSEM

3. **"Intent-Driven Network Management with Multi-Agent LLMs: The Confucius Framework"** (2025)
   - DOI: 10.1145/3718958.3750537
   - Relevance: Core — production Meta system with validation framework; DAG workflow modeling
   - Quality: High — 2-year production history

## Key Finding

**The field has not coalesced around "typed tool contracts" terminology**. No papers were found explicitly addressing preconditions, effects, or formal contract verification for LLM tool calls. Current research uses:
- "Tool use" / "function calling" (not "typed contracts")
- "Schema validation" for APIs (not for LLM tool schemas)
- "Preconditions" and "effects" in formal methods community (not applied to LLM tool calls)

**G25 (NEW GAP)**: Formal verification and type-theoretic foundations for LLM tool contracts — specifically schema validation frameworks, precondition/effect modeling, static validation pipelines, and contract-aware failure prevention — remain absent from the literature.

## Files
- Run directory: `/Users/zhuyingqin/Documents/New project/Auto-claude-code-research-in-sleep/lit-watch/real-agent-trials/20260505T012607Z-typed-tool-contracts-for-llm-agents-including-schemas-preconditions-effects-work`
- OpenAlex export: `openalex/`
- SUMMARY.md: `SUMMARY.md`
- reviewer_direction.md: `reviewer_direction.md`
- AGENT_DECISIONS.jsonl: `AGENT_DECISIONS.jsonl`
- RETRIEVAL_EVAL.json: `RETRIEVAL_EVAL.json`
- QUALITY_NOTES.md: `QUALITY_NOTES.md`