# WorkflowIR LitSearch Effectiveness Report

This report compares the free-form baseline agent batch with the WorkflowIR workflow batch on the same topic set.

## Metrics

| Metric | Baseline | WorkflowIR | Delta |
|---|---:|---:|---:|
| completion_rate | 0.00% | 100.00% | 100.00% |
| timeout_rate | 100.00% | 0.00% | -100.00% |
| contract_pass_rate | n/a | 100.00% | n/a |
| full_export_rate | n/a | 100.00% | n/a |

## Interpretation

- Baseline measures free-form agent execution reliability.
- WorkflowIR measures the same retrieval task with explicit node contracts, deterministic OpenAlex execution, query repair, and artifact verification.
- A higher WorkflowIR completion/contract rate supports the claim that structured workflow control improves agent reliability.

## Artifacts

- Machine-readable comparison: `data/workflowir_litsearch_eval/effectiveness_comparison.json`
