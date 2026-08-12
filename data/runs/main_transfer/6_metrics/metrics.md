# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs.

Records: 900 (clean=0, attack=900)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 50
- indirect_injection: 50
- policy_retrieval: 50

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.113 [0.080, 0.150] | — | 0.113 [0.080, 0.150] | 0.827 [0.783, 0.870] | — |
| G1 | 0.093 [0.063, 0.127] | — | 0.093 [0.060, 0.127] | 0.830 [0.787, 0.873] | — |
| G2 | 0.000 [0.000, 0.000] | — | 0.000 [0.000, 0.000] | 0.793 [0.747, 0.837] | — |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.190 [0.120, 0.270] | 0.190 [0.120, 0.270] | 0.000 [0.000, 0.000] |
| indirect_injection | 0.150 [0.080, 0.220] | 0.090 [0.040, 0.150] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.133 [0.080, 0.187] | 0.113 [0.067, 0.167] | 0.000 [0.000, 0.000] |
| nova-pro | 0.093 [0.047, 0.147] | 0.073 [0.033, 0.120] | 0.000 [0.000, 0.000] |
