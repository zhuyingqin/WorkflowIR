# Research Idea Report: LLM Tool Use and Workflow Automation

**Direction:** 从 ReAct 式下一步工具调用，转向 planner、DAG tool plan、tool selection、workflow synthesis、program synthesis
**Generated:** 2026-05-04
**Language:** Chinese
**Ideas evaluated:** 8 generated -> 5 recommended -> 0 piloted
**Pilot status:** skipped; this pass is a paper-level idea generation and quick novelty scan.

## Landscape Summary

本地 AAAI 2026 的 9 篇工具使用与 workflow 自动化论文已经形成一个很清楚的迁移方向：agent 不再只是 `Thought -> Action -> Observation` 的循环，而是在显式结构上工作，包括 DAG、workflow graph、tool transition graph、program、pipeline 和 distributed communication graph。

这条线的关键代表包括：`Beyond ReAct` 把复杂工具推理转为 planner-centric DAG planning；`AutoTool` 用历史工具轨迹中的 low-entropy inertia 降低 tool selection 成本；`TAPA` 把 agent adaptation 转为 LLM-guided program synthesis；`DiffAgent` 把代码生成、调试、搜索和执行反馈连成闭环；`DAWN` 把多 agent communication graph 当成可学习的 workflow 对象。

近期相关工作也在强化这个趋势。`Flow` 把 multi-agent workflow 表示成 AOV graph，并在执行中动态调整；`AutoFlow` 自动生成 natural-language workflow；`WorfBench` 专门评估 LLM 生成 DAG workflow 的能力；`AgentSquare` 在 Planning、Reasoning、Tool Use、Memory 的模块化空间中自动搜索 agent 架构；`Halo` 进一步把 agentic workflow 当成 query-plan DAG 做系统级批处理优化。

但是这些工作中仍有一个核心缺口：大部分方法把 workflow 当成“模型输出的图”或“执行时的经验轨迹”，还没有充分把它当成一种 **可编译、可静态检查、可局部修复、可跨任务复用的中间表示**。这给我们留下了最有价值的创新空间。

## Recommended Ideas

### Idea 1: Agent Workflow Compiler with Typed Intermediate Representation

- **一句话:** 把 LLM 生成的工具计划编译成 typed workflow IR，并在执行前做静态检查、代价优化和安全约束验证。
- **核心假设:** 相比直接执行自然语言计划或 DAG，带有类型、前置条件、后置条件、数据流和资源预算的 workflow IR 能显著减少无效工具调用、参数错误、依赖错误和执行时回滚。
- **方法雏形:** 设计一个 `WorkflowIR`，节点是 tool/program/LLM-call，边是 data dependency/control dependency，节点带 schema、precondition、effect、cost、risk level。然后实现 compiler passes：type check、dependency check、dead-step elimination、parallelization、budget-aware scheduling、safety gate。最后把 IR 编译到 LangGraph、MCP tool calls 或 Python executor。
- **最小实验:** 在 StableToolBench、ToolBench 或一个可控 multi-tool sandbox 上比较 `ReAct`、`Beyond-ReAct-style DAG planner`、`WorkflowIR compiler`。指标包括 success rate、invalid tool call rate、token cost、execution latency、recovery count。
- **新颖性:** `Beyond ReAct` 有 DAG plan，但缺少 typed compiler-style static analysis；`Flow` 有 AOV graph 动态调整，但不是面向工具 schema 和执行契约的 compiler；`AutoFlow` 生成 natural-language workflow，但缺少强 IR 和静态验证。
- **风险:** MEDIUM。挑战在于 IR 设计不能过重，否则会变成工程系统而不是论文方法。
- **贡献类型:** new method + system + benchmark diagnostics。
- **为什么值得做:** 这是最像“下一代 agent runtime”的方向。它把 planner、tool selection、workflow synthesis、program synthesis 统一到一个中间层。

### Idea 2: Counterexample-Guided Workflow Repair for Tool-Using Agents

- **一句话:** 执行失败时，不让 LLM 整体重想，而是把 tool observation 变成 counterexample，定位 DAG 中最小错误子图并局部修复。
- **核心假设:** 大多数复杂工具计划失败不是因为全局目标错了，而是因为局部依赖、参数、前置条件或顺序错了；最小子图修复会比 ReAct retry 或 whole-plan regeneration 更稳、更省。
- **方法雏形:** 先生成 DAG/WorkflowIR，再运行 verifier。若工具返回错误、空结果、schema mismatch、constraint violation，就构造 counterexample trace。repair model 只允许修改相关 node/edge/argument，并用 edit distance 或 graph patch penalty 控制最小修改。
- **最小实验:** 构造一组带故障注入的 tool-use tasks：缺参、错参、工具不可用、输出格式变化、前置条件未满足。比较 full replanning、ReAct retry、局部 workflow repair。
- **新颖性:** `DiffAgent` 和 `QualityFlow` 都有调试/质量检查闭环，但更偏程序合成；`Flow` 有动态 refinement，但没有 counterexample-guided minimal graph patch 的形式化机制。
- **风险:** LOW-MEDIUM。实现可以先从 schema/tool errors 开始，不必一开始覆盖所有语义错误。
- **贡献类型:** new method + diagnostic benchmark。
- **为什么值得做:** 这是非常容易讲清楚的创新点：从“失败后重试”变成“失败后定位和修补 workflow”。

### Idea 3: Trace-to-Workflow Mining: Discover Reusable Sub-DAGs from Agent Trajectories

- **一句话:** 从大量 ReAct/agent 执行轨迹中挖掘可复用子流程，把高频工具序列升级成有 guard conditions 的 workflow macro 或 meta-tool。
- **核心假设:** agent 轨迹里不仅存在 `AutoTool` 说的 next-tool inertia，还存在更长程的 reusable workflow motifs；把这些 motifs 编译成 macro 可以同时提高成功率、降低成本、减少长链错误传播。
- **方法雏形:** 对轨迹做 process mining / frequent subgraph mining，抽取候选 sub-DAG；学习每个 sub-DAG 的适用条件、输入输出 schema、失败模式；把它封装成 meta-tool 或 workflow template。运行时先检索相关 macro，再由 planner 组合宏和原子工具。
- **最小实验:** 用 ALFWorld、ScienceWorld、ToolQuery、ToolBench 或自建浏览器/代码任务轨迹。比较 ReAct、AutoTool、AWO-style meta-tool、ours guarded sub-DAG mining。
- **新颖性:** `AutoTool` 主要预测下一工具；`AWO` 把冗余工具序列合成 meta-tool；我们的差异是挖掘带数据依赖、分支、前置条件和失败恢复的 reusable sub-DAG。
- **风险:** MEDIUM。需要足够多的轨迹；可以先用现有 benchmark 自动生成轨迹。
- **贡献类型:** new method + empirical finding。
- **为什么值得做:** 这是最实用的方向之一，容易和成本、效率、可复用性挂钩。

### Idea 4: Contract Learning for Tools: From Tool Cards to Learned Preconditions and Effects

- **一句话:** 自动从工具文档、schema 和执行轨迹中学习 tool contract，用于 planner 的可行性检查和参数生成。
- **核心假设:** 现有 agent 经常失败于“不知道工具什么时候可用、输出能喂给谁、失败意味着什么”。如果每个工具都有 learned contract，planner 就能在生成 DAG 前过滤不可行组合。
- **方法雏形:** 对每个 tool 学习 `input type`、`latent precondition`、`output effect`、`failure signature`、`downstream compatibility`。来源包括 tool docs、schema、历史成功/失败轨迹。planner 生成计划时把 contract 作为 hard/soft constraints。
- **最小实验:** 在 multi-tool QA、web automation 或 software-dev tools 上记录错误类型，看 contract-aware planner 是否减少 invalid transitions 和 useless calls。
- **新颖性:** `OctoTools` 等工作使用 tool cards；`AutoTool` 使用工具转移图；这个 idea 的重点是把工具能力变成可学习的 planning contract，并用于静态/动态验证。
- **风险:** LOW-MEDIUM。第一版可以只学习 schema compatibility 和 frequent failure rules。
- **贡献类型:** new method + interpretability/diagnostic。
- **为什么值得做:** 它可以作为 Idea 1 的关键模块，也能单独成文。

### Idea 5: Budget-Aware Workflow Optimizer for Agent Plans

- **一句话:** 给 agent workflow 加一个 cost model，在成功率、token、latency、并行度和工具费用之间自动做计划优化。
- **核心假设:** 很多 agent 论文只比 success rate，但真实 workflow 需要在 SLA、成本和可靠性之间平衡；显式 cost model 能让 planner 选择更合适的工具路径。
- **方法雏形:** 学习或估计每个 node 的 LLM cost、tool latency、failure probability、retry cost、cacheability。对 DAG 做重排、并行化、LLM-call fusion、cheap-tool-first probing、expensive-tool gating。
- **最小实验:** 在 batch 多任务场景、research workflow 或 data-analysis workflow 上比较普通 DAG planning 与 cost-aware scheduling。
- **新颖性:** `Halo` 已经做 agentic workflow 的系统级 batch query optimization；我们的区别可以放在 single-agent/multi-agent planning 层，关注工具选择、失败概率和语义质量，而不只是 serving-level GPU/KV-cache 优化。
- **风险:** MEDIUM。容易被认为是系统工程，需要有清晰算法和消融。
- **贡献类型:** system + method。
- **为什么值得做:** 如果目标是落地 agent，这是非常强的现实卖点。

## Secondary Ideas

### Idea 6: Federated Workflow Memory for Organizations

- **核心:** 多个组织不共享原始任务数据，只共享压缩后的 workflow motif、tool contract 或失败模式，形成 privacy-preserving workflow memory。
- **连接工作:** 继承 `DAWN` 的 federated workflow synthesis，但把目标从 communication graph 扩展到 reusable tool workflows。
- **风险:** HIGH。实验搭建复杂，审稿人会追问隐私保证和真实组织场景。

### Idea 7: Workflow-Level Credit Assignment for Planner Training

- **核心:** 不只用最终 success/failure 训练 planner，而是把奖励分配到 DAG 的节点、边、参数和 repair action。
- **连接工作:** 扩展 `Beyond ReAct` 的 SFT+GRPO 和 `AgentFlow` 的 in-the-flow optimization。
- **风险:** HIGH。训练成本和基线复杂度较高，但如果成功会很有分量。

### Idea 8: Executable Workflow Benchmark with Loops, Branches, Failure, and Budget

- **核心:** 构建比 DAG exact match 更真实的 workflow benchmark，包含可执行工具、分支、循环、失败恢复和预算约束。
- **连接工作:** 扩展 `WorfBench` / `ComplexTool-Plan`，从 graph generation 走向 executable operational semantics。
- **风险:** MEDIUM-HIGH。Benchmark 工作需要规模、质量和社区接受度。

## Ranking

| Rank | Idea | Novelty | Feasibility | Impact | Overall |
|---:|---|---:|---:|---:|---:|
| 1 | Agent Workflow Compiler with Typed IR | 9 | 7 | 9 | 25 |
| 2 | Counterexample-Guided Workflow Repair | 8 | 8 | 8 | 24 |
| 3 | Trace-to-Workflow Mining | 8 | 7 | 8 | 23 |
| 4 | Contract Learning for Tools | 7 | 8 | 7 | 22 |
| 5 | Budget-Aware Workflow Optimizer | 7 | 7 | 8 | 22 |
| 6 | Workflow-Level Credit Assignment | 8 | 5 | 9 | 22 |
| 7 | Executable Workflow Benchmark | 7 | 6 | 8 | 21 |
| 8 | Federated Workflow Memory | 8 | 4 | 8 | 20 |

## Recommended Main Direction

我建议主线做：

**WorkflowIR: A Typed, Verifiable, and Self-Repairing Intermediate Representation for LLM Tool Workflows**

这条主线可以自然合并 Idea 1、2、4，并把 Idea 3 作为扩展模块：

1. Planner 生成 `WorkflowIR`，不是直接输出工具调用。
2. Compiler 对 IR 做 type/dataflow/precondition/cost/safety 检查。
3. Executor 执行 IR，并记录 structured trace。
4. Failure analyzer 把失败转为 counterexample。
5. Repair module 对 IR 做最小 patch。
6. Trace miner 把成功 IR 子图沉淀为 workflow library。

## Concrete Paper Claim

一个可以写进论文摘要的 claim：

> Existing tool-using LLM agents either react step-by-step or generate unverified workflow graphs. We propose a compiler-style agent architecture that represents tool workflows as a typed intermediate representation, enabling static validation, cost-aware optimization, and counterexample-guided repair before and during execution.

## Minimum Viable Experiment Plan

### MVP-1: Controlled Tool Sandbox

- 设计 30-50 个任务，包含 10-20 个工具。
- 每个工具有 schema、precondition、effect 和 failure mode。
- 构造需要串行、并行、分支和 recovery 的任务。
- 比较 ReAct、Plan-and-Execute、DAG-only planner、WorkflowIR。

### MVP-2: Existing Benchmark Transfer

- 选择 StableToolBench、ToolBench、ScienceWorld 或 ToolQuery-Academic。
- 不需要训练大模型，先用 prompting + verifier + repair。
- 指标：success rate、invalid action rate、token cost、tool calls、latency、repair success。

### MVP-3: Ablation

- remove type checker
- remove precondition checker
- remove repair
- remove cost optimizer
- replace IR with plain natural language plan
- replace local repair with whole-plan regeneration

## Expected Reviewer Objections

| Objection | Response |
|---|---|
| 这只是工程系统，不是算法创新 | 强调 IR formalization、compiler passes、counterexample-guided graph repair 和可诊断指标 |
| typed contract 太人工 | 第一版允许从 schema/docs 自动抽取，人工只用于 benchmark ground truth |
| DAG 不支持循环和动态分支 | IR 可以先支持 DAG + conditional edge，后续扩展 loop；论文主实验聚焦复杂但可控 workflow |
| 与 Flow/AutoFlow/Beyond ReAct 太接近 | 差异是 compile-time validation + execution-time minimal repair，而不是只生成/调整 workflow |
| benchmark 不够真实 | 同时使用可控 sandbox 和现有 benchmark，报告错误类型分解 |

## Eliminated or Deprioritized Ideas

| Idea | Reason |
|---|---|
| 只做更大的 DAG planner | `Beyond ReAct` 已经很接近，增量不够明显 |
| 只做 tool selection graph | `AutoTool` 和 `SIT-Graph` 已经覆盖较多，需要加入 state/contract/repair 才有新意 |
| 只做 workflow benchmark | 有价值，但缺方法容易变成资源型工作 |
| 只做 multi-agent communication graph | `DAWN` 已经很强，除非结合 privacy-preserving workflow memory |
| 只做 program synthesis agent | `TAPA`、`QualityFlow`、SEIDR 等相关工作较多，需要放到 workflow IR/repair 下才更有差异 |

## Sources Used

- Local AAAI 2026 analysis: `awesome-aaai-2026-papers/llm-agents-tool-use/TOOL_WORKFLOW_AUTOMATION_DETAILED_ANALYSIS.md`
- ReAct: https://arxiv.org/abs/2210.03629
- Beyond ReAct: https://arxiv.org/abs/2511.10037
- AutoTool: https://arxiv.org/abs/2511.14650
- Flow: https://proceedings.iclr.cc/paper_files/paper/2025/hash/ba84da6921f3040b74ee163aa7451f53-Abstract-Conference.html
- AutoFlow: https://arxiv.org/abs/2407.12821
- AgentSquare: https://proceedings.iclr.cc/paper_files/paper/2025/hash/0ae94013da7cd459402fd77874e09ee3-Abstract-Conference.html
- WorfBench: https://openreview.net/pdf/1d331e547b7dab39a01832803d3bcfd7ff5d447d.pdf
- QualityFlow: https://arxiv.org/abs/2501.17167
- Halo: https://arxiv.org/abs/2509.02121
- Agent Workflow Optimization / Meta-tools: https://arxiv.org/abs/2601.22037

## Next Steps

1. 对 `WorkflowIR + static validation + counterexample repair` 做 novelty-check。
2. 设计最小 sandbox：工具 schema、任务集、错误类型、评价指标。
3. 先用 GPT/Claude/Qwen API 做 prompting 版，无需训练。
4. 如果 pilot 有信号，再考虑 planner SFT/RL 或 trace mining 扩展。
