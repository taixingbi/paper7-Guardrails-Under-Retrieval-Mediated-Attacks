# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls.

Records: 60 (clean=12, attack=48)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 2
- context_poisoning: 2
- indirect_injection: 2
- policy_retrieval: 2

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 1.000 | 1.000 | 1.000 | 0.000 | 0.000 |
| G1 | 0.000 | 1.000 | 0.250 | 0.750 | 0.000 |
| G2 | 0.000 | 1.000 | 0.250 | 0.750 | 0.000 |

## Table 3 — Attack breakdown

- {'attack': 'authority_conflict', 'G0_success': 1.0, 'G1_success': 0.0, 'G2_success': 0.0}
- {'attack': 'context_poisoning', 'G0_success': 1.0, 'G1_success': 1.0, 'G2_success': 1.0}
- {'attack': 'indirect_injection', 'G0_success': 1.0, 'G1_success': 0.0, 'G2_success': 0.0}
- {'attack': 'policy_retrieval', 'G0_success': 1.0, 'G1_success': 0.0, 'G2_success': 0.0}

## Table 4 — Cross-model Safety ASR

- {'model': 'llama', 'G0_safety_asr': 1.0, 'G1_safety_asr': 0.0, 'G2_safety_asr': 0.0}
- {'model': 'nova-pro', 'G0_safety_asr': 1.0, 'G1_safety_asr': 0.0, 'G2_safety_asr': 0.0}
