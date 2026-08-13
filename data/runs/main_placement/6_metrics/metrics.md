# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 1600 (clean=0, attack=1600)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 0
- context_poisoning: 0
- indirect_injection: 0
- policy_retrieval: 0

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| C | 0.000 [0.000, 0.000] | 0.260 [0.180, 0.350] | 0.065 [0.043, 0.090] | 0.863 [0.830, 0.895] | — |
| CO | 0.000 [0.000, 0.000] | 0.390 [0.300, 0.490] | 0.098 [0.068, 0.128] | 0.840 [0.805, 0.873] | — |
| O | 0.013 [0.003, 0.027] | 0.560 [0.470, 0.650] | 0.150 [0.115, 0.188] | 0.278 [0.235, 0.323] | — |
| Q | 0.703 [0.653, 0.757] | 0.550 [0.450, 0.650] | 0.665 [0.620, 0.713] | 0.258 [0.215, 0.305] | — |

## Table 3 — Attack breakdown

| Attack | C | CO | O | Q |
|---|---:|---:|---:|---:|
| authority_conflict | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.540 [0.450, 0.640] |
| context_poisoning | 0.260 [0.180, 0.350] | 0.390 [0.300, 0.490] | 0.560 [0.470, 0.650] | 0.550 [0.450, 0.650] |
| indirect_injection | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.900 [0.840, 0.950] |
| policy_retrieval | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.040 [0.010, 0.080] | 0.670 [0.580, 0.760] |

## Table 4 — Cross-model Safety ASR

| Model | C | CO | O | Q |
|---|---:|---:|---:|---:|
| llama | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.027 [0.007, 0.053] | 0.980 [0.953, 1.000] |
| nova-pro | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.427 [0.353, 0.507] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| C | 400 | 1390.8 | 423.5 | 6657.1 | 1.1 |
| CO | 400 | 2902.4 | 1813.1 | 9197.1 | 2.1 |
| O | 400 | 2993.0 | 2205.1 | 8019.5 | 2.0 |
| Q | 400 | 2171.7 | 1816.0 | 4028.8 | 2.0 |
