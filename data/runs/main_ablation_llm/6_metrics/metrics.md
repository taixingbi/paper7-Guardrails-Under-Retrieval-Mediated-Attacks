# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls.

Records: 3000 (clean=600, attack=2400)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 100
- context_poisoning: 100
- indirect_injection: 100
- policy_retrieval: 100

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.685 | 0.530 | 0.646 | 0.279 | 0.000 |
| G1 | 0.457 | 0.335 | 0.426 | 0.393 | 0.000 |
| G2 | 0.007 | 0.355 | 0.094 | 0.389 | 0.015 |

## Table 3 — Attack breakdown

- {'attack': 'authority_conflict', 'G0_success': 0.545, 'G1_success': 0.24, 'G2_success': 0.0}
- {'attack': 'context_poisoning', 'G0_success': 0.53, 'G1_success': 0.335, 'G2_success': 0.355}
- {'attack': 'indirect_injection', 'G0_success': 0.905, 'G1_success': 0.72, 'G2_success': 0.0}
- {'attack': 'policy_retrieval', 'G0_success': 0.605, 'G1_success': 0.41, 'G2_success': 0.02}

## Table 4 — Cross-model Safety ASR

- {'model': 'llama', 'G0_safety_asr': 0.9766666666666667, 'G1_safety_asr': 0.6366666666666667, 'G2_safety_asr': 0.013333333333333334}
- {'model': 'nova-pro', 'G0_safety_asr': 0.3933333333333333, 'G1_safety_asr': 0.27666666666666667, 'G2_safety_asr': 0.0}
