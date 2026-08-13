# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 1500 (clean=300, attack=1200)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 50
- context_poisoning: 50
- indirect_injection: 50
- policy_retrieval: 50

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.460 [0.403, 0.517] | 0.570 [0.470, 0.670] | 0.487 [0.438, 0.537] | 0.395 [0.350, 0.445] | 0.000 [0.000, 0.000] |
| G1 | 0.000 [0.000, 0.000] | 0.290 [0.200, 0.380] | 0.072 [0.048, 0.098] | 0.792 [0.752, 0.830] | 0.000 [0.000, 0.000] |
| G2 | 0.000 [0.000, 0.000] | 0.270 [0.190, 0.360] | 0.068 [0.043, 0.092] | 0.815 [0.777, 0.853] | 0.020 [0.000, 0.050] |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.540 [0.450, 0.640] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.570 [0.480, 0.670] | 0.290 [0.200, 0.380] | 0.270 [0.180, 0.350] |
| indirect_injection | 0.690 [0.600, 0.780] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.150 [0.080, 0.230] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.700 [0.627, 0.773] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| nova-pro | 0.220 [0.153, 0.293] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G0 | 500 | 1269.4 | 512.3 | 5155.0 | 1.0 |
| G1 | 500 | 2168.1 | 1447.7 | 7141.0 | 1.3 |
| G2 | 500 | 3716.3 | 2876.7 | 9646.3 | 2.2 |
