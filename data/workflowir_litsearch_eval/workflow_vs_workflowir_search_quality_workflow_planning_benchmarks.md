# Workflow vs WorkflowIR Search Quality Evaluation

Topic: benchmarks for tool-using LLM agents that evaluate DAG planning, executable workflows, API-tool selection, dependency edges, and exact-match workflow plans

## Inputs

- Workflow run: `/Users/zhuyingqin/Documents/New project/Auto-claude-code-research-in-sleep/lit-watch/real-agent-trials/20260505T020439Z-benchmarks-for-tool-using-llm-agents-that-evaluate-dag-planning-executable-workf`
- WorkflowIR run: `/Users/zhuyingqin/Documents/New project/Auto-claude-code-research-in-sleep/lit-watch/workflowir-agent-runs/20260505T052505Z-benchmarks-for-tool-using-llm-agents-that-evaluate-dag-planning-executable-workflows-api-tool-se`
- Machine-readable report: `data/workflowir_litsearch_eval/workflow_vs_workflowir_search_quality_workflow_planning_benchmarks.json`

## Metric Comparison

| Metric | Workflow | WorkflowIR | Delta | Note |
|---|---:|---:|---:|---|
| Coverage size | 348 | 112 | -236 | larger is broader, not always better |
| Query families | 5 | 5 | 0 | 2-5 is expected |
| Too-broad queries | 0 | 0 | 0 | lower is better |
| Zero-result queries | 0 | 0 | 0 | lower is better |
| Mean relevance@k | 48.4% | 54.0% | 5.5% | higher is better |
| Core@k | 0.0% | 5.0% | 5.0% | higher is better |
| Core/supporting@k | 100.0% | 100.0% | 0.0% | higher is better |
| Off-topic@k | 0.0% | 0.0% | 0.0% | lower is better |
| Anchor coverage@k | 66.7% | 50.0% | -16.7% | higher is better |
| Mean quality@k | 83.4% | 79.7% | -3.8% | higher is better |
| Mean combined@k | 60.7% | 63.0% | 2.3% | higher is better |
| Audit artifacts present | 3 | 11 | 8 | higher is better for auditability |
| Artifact pass rate | 100.0% | 100.0% | 0.0% | higher is better |

## Top Retrieved Papers

| Rank | Workflow | Score | WorkflowIR | Score |
|---:|---|---:|---|---:|
| 1 | Large language models empowered agent-based modeling and simulation: a survey and perspectives | 70.4% | MedAgentBench: A Virtual EHR Environment to Benchmark Medical LLM Agents | 76.1% |
| 2 | MedAgentBench: A Virtual EHR Environment to Benchmark Medical LLM Agents | 69.0% | LLM-Based Agents for Tool Learning: A Survey | 68.6% |
| 3 | Artificial Intelligence agents for biological research: a survey | 65.2% | Large Language Model Agents for Biomedicine: A Comprehensive Review of Methods, Evaluations, Challenges, and Future Directions | 66.1% |
| 4 | LLM Agents for Smart City Management: Enhancing Decision Support Through Multi-Agent AI Systems | 64.1% | Importance of investing time and money in integrating large language model-based agents into outbreak analytics pipelines | 65.8% |
| 5 | Agentic and LLM-Based Multimodal Anomaly Detection: Architectures, Challenges, and Prospects | 63.1% | Evaluating Faithfulness in Agentic RAG Systems for e-Governance Applications Using LLM-Based Judging Frameworks | 65.2% |
| 6 | Large language model agents can use tools to perform clinical calculations | 62.1% | CodeSim: Multi-Agent Code Generation and Problem Solving through Simulation-Driven Planning and Debugging | 64.4% |
| 7 | Insight Agents: An LLM-Based Multi-Agent System for Data Insights | 61.0% | Local Agentic RAG-Based Information SystemDevelopment for Intelligent Analysis of GitHubCode Repositories in Computer ScienceEducation | 63.1% |
| 8 | Exploring the Application of Large Language Models Based AI Agents in Leakage Detection of Natural Gas Valve Chambers | 60.2% | Operational Resilience Under Carbon Constraints: A Socio-Technical Multi-Agentic Approach to Global Supply Chains | 63.1% |
| 9 | BPMN-Based Design of Multi-Agent Systems: Personalized Language Learning Workflow Automation with RAG-Enhanced Knowledge Access | 59.5% | Efficient Multi-Agent Collaboration with Tool Use for Online Planning in Complex Table Question Answering | 62.3% |
| 10 | Swedish Medical LLM Benchmark: development and evaluation of a framework for assessing large language models in the Swedish medical domain | 59.1% | Large Language Model Agents for Biomedicine: A Comprehensive Review of Methods, Evaluations, Challenges, and Future Directions | 61.0% |

## Interpretation

- WorkflowIR produced a stronger audit trail because it generated more checkable intermediate artifacts.
- WorkflowIR is at least competitive on top-k semantic relevance under the shared heuristic.
- Workflow retrieved a broader pool; this can help recall, but it also increases manual screening cost.
