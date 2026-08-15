# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 300 (clean=0, attack=300)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 0
- indirect_injection: 0
- policy_retrieval: 0

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G1 | 0.100 [0.067, 0.137] | — | 0.100 [0.070, 0.137] | 0.560 [0.503, 0.617] | — |

## Table 3 — Attack breakdown

| Attack | G1 |
|---|---:|
| authority_conflict | 0.200 [0.130, 0.280] |
| indirect_injection | 0.100 [0.050, 0.160] |
| policy_retrieval | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G1 |
|---|---:|
| llama | 0.120 [0.073, 0.180] |
| nova-pro | 0.080 [0.040, 0.127] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G1 | 300 | 1803.2 | 1164.8 | 5310.0 | 1.4 |
