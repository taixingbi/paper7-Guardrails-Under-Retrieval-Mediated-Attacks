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
| G1 | 0.000 | 0.415 | 0.104 | 0.786 | 0.000 |
| G2 | 0.000 | 0.430 | 0.107 | 0.787 | 0.015 |

## Table 3 — Attack breakdown

- {'attack': 'authority_conflict', 'G0_success': 0.545, 'G1_success': 0.0, 'G2_success': 0.0}
- {'attack': 'context_poisoning', 'G0_success': 0.53, 'G1_success': 0.415, 'G2_success': 0.43}
- {'attack': 'indirect_injection', 'G0_success': 0.905, 'G1_success': 0.0, 'G2_success': 0.0}
- {'attack': 'policy_retrieval', 'G0_success': 0.605, 'G1_success': 0.0, 'G2_success': 0.0}

## Table 4 — Cross-model Safety ASR

- {'model': 'llama', 'G0_safety_asr': 0.9766666666666667, 'G1_safety_asr': 0.0, 'G2_safety_asr': 0.0}
- {'model': 'nova-pro', 'G0_safety_asr': 0.3933333333333333, 'G1_safety_asr': 0.0, 'G2_safety_asr': 0.0}
