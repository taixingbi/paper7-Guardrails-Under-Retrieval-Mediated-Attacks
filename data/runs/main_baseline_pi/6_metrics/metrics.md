# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 1300 (clean=100, attack=1200)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 50
- context_poisoning: 50
- indirect_injection: 50
- policy_retrieval: 50

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.697 [0.647, 0.753] | 0.510 [0.410, 0.610] | 0.650 [0.605, 0.698] | 0.275 [0.233, 0.320] | 0.000 [0.000, 0.000] |
| G1 | 0.403 [0.353, 0.463] | 0.550 [0.450, 0.650] | 0.440 [0.393, 0.487] | 0.470 [0.422, 0.520] | — |
| G2 | 0.007 [0.000, 0.017] | 0.560 [0.460, 0.660] | 0.145 [0.110, 0.180] | 0.475 [0.425, 0.527] | — |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.560 [0.470, 0.660] | 0.550 [0.450, 0.640] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.510 [0.420, 0.620] | 0.550 [0.450, 0.640] | 0.560 [0.470, 0.660] |
| indirect_injection | 0.900 [0.840, 0.950] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.630 [0.530, 0.720] | 0.660 [0.570, 0.750] | 0.020 [0.000, 0.050] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.987 [0.967, 1.000] | 0.660 [0.587, 0.740] | 0.013 [0.000, 0.033] |
| nova-pro | 0.407 [0.327, 0.487] | 0.147 [0.093, 0.207] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G0 | 500 | — | — | — | — |
| G1 | 400 | 1138.0 | 586.4 | 4484.5 | 1.0 |
| G2 | 400 | 3805.8 | 2811.8 | 9883.9 | 2.0 |
