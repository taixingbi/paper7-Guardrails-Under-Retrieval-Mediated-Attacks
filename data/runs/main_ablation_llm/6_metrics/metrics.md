# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs.

Records: 3000 (clean=600, attack=2400)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 100
- context_poisoning: 100
- indirect_injection: 100
- policy_retrieval: 100

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.685 [0.648, 0.723] | 0.530 [0.460, 0.600] | 0.646 [0.613, 0.679] | 0.279 [0.249, 0.310] | 0.000 [0.000, 0.000] |
| G1 | 0.457 [0.417, 0.497] | 0.335 [0.270, 0.405] | 0.426 [0.391, 0.461] | 0.393 [0.359, 0.426] | 0.000 [0.000, 0.000] |
| G2 | 0.007 [0.002, 0.013] | 0.355 [0.290, 0.420] | 0.094 [0.074, 0.115] | 0.389 [0.354, 0.424] | 0.015 [0.000, 0.035] |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.545 [0.475, 0.615] | 0.240 [0.185, 0.300] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.530 [0.460, 0.600] | 0.335 [0.270, 0.400] | 0.355 [0.290, 0.420] |
| indirect_injection | 0.905 [0.860, 0.945] | 0.720 [0.655, 0.780] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.605 [0.535, 0.670] | 0.410 [0.345, 0.480] | 0.020 [0.005, 0.040] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.977 [0.960, 0.993] | 0.637 [0.583, 0.690] | 0.013 [0.003, 0.027] |
| nova-pro | 0.393 [0.337, 0.450] | 0.277 [0.230, 0.327] | 0.000 [0.000, 0.000] |
