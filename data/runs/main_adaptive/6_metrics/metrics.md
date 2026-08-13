# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 900 (clean=0, attack=900)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 50
- indirect_injection: 50
- policy_retrieval: 50

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.343 [0.293, 0.397] | — | 0.343 [0.290, 0.400] | 0.697 [0.643, 0.750] | — |
| G1 | 0.327 [0.277, 0.380] | — | 0.327 [0.273, 0.380] | 0.677 [0.623, 0.730] | — |
| G2 | 0.000 [0.000, 0.000] | — | 0.000 [0.000, 0.000] | 0.580 [0.520, 0.637] | — |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.670 [0.580, 0.760] | 0.680 [0.590, 0.770] | 0.000 [0.000, 0.000] |
| indirect_injection | 0.360 [0.270, 0.450] | 0.300 [0.220, 0.390] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.333 [0.260, 0.407] | 0.327 [0.253, 0.407] | 0.000 [0.000, 0.000] |
| nova-pro | 0.353 [0.280, 0.433] | 0.327 [0.253, 0.400] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G0 | 300 | 483.1 | 448.2 | 734.5 | 1.0 |
| G1 | 300 | 4596.9 | 3752.1 | 10205.3 | 1.8 |
| G2 | 300 | 5915.8 | 5027.7 | 11784.8 | 2.8 |
