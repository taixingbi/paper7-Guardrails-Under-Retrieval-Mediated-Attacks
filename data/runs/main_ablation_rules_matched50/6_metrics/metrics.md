# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 1000 (clean=200, attack=800)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 0
- context_poisoning: 0
- indirect_injection: 0
- policy_retrieval: 0

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G1 | 0.000 [0.000, 0.000] | 0.400 [0.310, 0.490] | 0.100 [0.072, 0.133] | 0.825 [0.787, 0.860] | 0.000 [0.000, 0.000] |
| G2 | 0.000 [0.000, 0.000] | 0.420 [0.330, 0.520] | 0.105 [0.077, 0.138] | 0.830 [0.792, 0.865] | 0.000 [0.000, 0.000] |

## Table 3 — Attack breakdown

| Attack | G1 | G2 |
|---|---:|---:|
| authority_conflict | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.400 [0.300, 0.490] | 0.420 [0.330, 0.520] |
| indirect_injection | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G1 | G2 |
|---|---:|---:|
| llama | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| nova-pro | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G1 | 500 | — | — | — | — |
| G2 | 500 | — | — | — | — |
