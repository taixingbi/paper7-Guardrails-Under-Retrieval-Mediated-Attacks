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
| G1 | 0.107 [0.077, 0.143] | — | 0.107 [0.073, 0.143] | 0.617 [0.563, 0.670] | — |

## Table 3 — Attack breakdown

| Attack | G1 |
|---|---:|
| authority_conflict | 0.190 [0.120, 0.270] |
| indirect_injection | 0.130 [0.070, 0.200] |
| policy_retrieval | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G1 |
|---|---:|
| llama | 0.127 [0.080, 0.180] |
| nova-pro | 0.087 [0.047, 0.133] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G1 | 300 | 1739.2 | 908.8 | 7026.6 | 1.8 |
