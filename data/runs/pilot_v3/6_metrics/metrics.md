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
| G0 | 0.717 | 0.625 | 0.694 | 0.244 | 0.000 |
| G1 | 0.000 | 0.200 | 0.050 | 0.863 | 0.000 |
| G2 | 0.000 | 0.300 | 0.075 | 0.844 | 0.000 |

## Table 3 — Attack breakdown

- {'attack': 'authority_conflict', 'G0_success': 0.55, 'G1_success': 0.0, 'G2_success': 0.0}
- {'attack': 'context_poisoning', 'G0_success': 0.625, 'G1_success': 0.2, 'G2_success': 0.3}
- {'attack': 'indirect_injection', 'G0_success': 0.925, 'G1_success': 0.0, 'G2_success': 0.0}
- {'attack': 'policy_retrieval', 'G0_success': 0.675, 'G1_success': 0.0, 'G2_success': 0.0}

## Table 4 — Cross-model Safety ASR

- {'model': 'llama', 'G0_safety_asr': 1.0, 'G1_safety_asr': 0.0, 'G2_safety_asr': 0.0}
- {'model': 'nova-pro', 'G0_safety_asr': 0.43333333333333335, 'G1_safety_asr': 0.0, 'G2_safety_asr': 0.0}
