# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls.

Records: 600 (clean=120, attack=480)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 20
- context_poisoning: 20
- indirect_injection: 20
- policy_retrieval: 20

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.717 | 0.600 | 0.688 | 0.256 | 0.000 |
| G1 | 0.725 | 0.575 | 0.688 | 0.263 | 0.000 |
| G2 | 0.017 | 0.575 | 0.156 | 0.275 | 0.000 |

## Table 3 — Attack breakdown

- {'attack': 'authority_conflict', 'G0_success': 0.55, 'G1_success': 0.55, 'G2_success': 0.0}
- {'attack': 'context_poisoning', 'G0_success': 0.6, 'G1_success': 0.575, 'G2_success': 0.575}
- {'attack': 'indirect_injection', 'G0_success': 0.925, 'G1_success': 0.925, 'G2_success': 0.0}
- {'attack': 'policy_retrieval', 'G0_success': 0.675, 'G1_success': 0.7, 'G2_success': 0.05}

## Table 4 — Cross-model Safety ASR

- {'model': 'llama', 'G0_safety_asr': 1.0, 'G1_safety_asr': 0.9666666666666667, 'G2_safety_asr': 0.03333333333333333}
- {'model': 'nova-pro', 'G0_safety_asr': 0.43333333333333335, 'G1_safety_asr': 0.48333333333333334, 'G2_safety_asr': 0.0}
