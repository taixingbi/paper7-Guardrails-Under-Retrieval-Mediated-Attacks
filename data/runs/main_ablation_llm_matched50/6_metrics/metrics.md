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
| G1 | 0.440 [0.383, 0.493] | 0.320 [0.230, 0.420] | 0.410 [0.362, 0.460] | 0.427 [0.383, 0.480] | 0.000 [0.000, 0.000] |
| G2 | 0.003 [0.000, 0.010] | 0.360 [0.270, 0.460] | 0.092 [0.065, 0.122] | 0.388 [0.343, 0.438] | 0.000 [0.000, 0.000] |

## Table 3 — Attack breakdown

| Attack | G1 | G2 |
|---|---:|---:|
| authority_conflict | 0.210 [0.130, 0.290] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.320 [0.230, 0.410] | 0.360 [0.270, 0.450] |
| indirect_injection | 0.740 [0.650, 0.820] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.370 [0.280, 0.470] | 0.010 [0.000, 0.030] |

## Table 4 — Cross-model Safety ASR

| Model | G1 | G2 |
|---|---:|---:|
| llama | 0.573 [0.493, 0.653] | 0.007 [0.000, 0.020] |
| nova-pro | 0.307 [0.240, 0.380] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G1 | 500 | — | — | — | — |
| G2 | 500 | — | — | — | — |
