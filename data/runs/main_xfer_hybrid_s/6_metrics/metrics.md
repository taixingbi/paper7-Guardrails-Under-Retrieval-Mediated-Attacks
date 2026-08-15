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
| G1 | 0.047 [0.023, 0.070] | — | 0.047 [0.027, 0.070] | 0.540 [0.483, 0.597] | — |

## Table 3 — Attack breakdown

| Attack | G1 |
|---|---:|
| authority_conflict | 0.090 [0.040, 0.150] |
| indirect_injection | 0.050 [0.010, 0.100] |
| policy_retrieval | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G1 |
|---|---:|
| llama | 0.067 [0.027, 0.107] |
| nova-pro | 0.027 [0.007, 0.053] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G1 | 300 | 1722.4 | 1159.2 | 5697.2 | 1.1 |
