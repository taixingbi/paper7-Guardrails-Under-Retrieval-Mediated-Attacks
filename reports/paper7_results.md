# Paper 7 Results Report

Generated from frozen main + input ablations + held-out transfer. Regenerate with `gurma paper-report`. Brackets are 95% bootstrap CIs.

## Setup

- Seeds: 100 HotpotQA (both-model clean freeze)
- Attacks: 4 × 100 = 400 validated cases (`accepted = semantic ∧ payload`)
- Guardrails: G0 none / G1 input / G2 input+output
- Models: `nova-pro`, `llama`; guard/judge: `gpt-oss`
- Defense freeze: hybrid input (`rules` first) + `v3` prompts ([FREEZE.md](../FREEZE.md))
- Main conditions: 3000 (2400 attack + 600 clean); API calls ≫ 3000
- Experiment 4: 50 frozen seeds × A1/A3/A4 held-out templates (generator=`deepseek`) × G0/G1/G2 × 2 models; defense not retuned

## Findings

1. **G0 is highly vulnerable** to retrieval-mediated instruction attacks (Safety ASR 0.685; A1 = 0.905). Llama is much weaker than Nova Pro on G0 (0.977 vs 0.393).
2. **Hybrid G1 eliminates in-distribution instruction/safety attacks** (Safety ASR 0.000) and raises attacked-task accuracy 0.279 → 0.820 with ~0 over-refusal.
3. **G2 adds almost nothing on hybrid** (rescue 10/517 G0 successes after G1). G2 rewrite is rare (11), so accuracy is not rewrite-inflated.
4. **Ablation:** rules-only also reaches Safety ASR 0.000; LLM-only remains 0.457. Hybrid mainly improves **PSR** vs rules (0.300 vs 0.415).
5. **Limitation:** context poisoning remains (PSR ≈ 0.30 under hybrid G1/G2). This is an integrity leftover, not a missing instruction filter.
6. **Transfer:** unseen templates mostly evade frozen rules (G1 allow ≈ 83%). G0 Safety ASR is 0.113; G1 only drops it to 0.093; G2 brings it to 0.000. Deterministic filters work on known structures; defense-in-depth matters under novel phrasing.

## Table 1 — Dataset

| Attack | Cases |
|---|---:|
| A1 Indirect injection | 100 |
| A2 Context poisoning | 100 |
| A3 Policy-violating retrieval | 100 |
| A4 Authority conflict | 100 |

## Table 2 — Main result (hybrid v3)

| Guardrail | Safety ASR ↓ | PSR ↓ | Macro ↓ | Acc ↑ | Over-refusal ↓ |
|---|---:|---:|---:|---:|---:|
| G0 | 0.685 [0.648, 0.723] | 0.530 [0.460, 0.600] | 0.646 [0.613, 0.679] | 0.279 [0.249, 0.310] | 0.000 [0.000, 0.000] |
| G1 | 0.000 [0.000, 0.000] | 0.300 [0.235, 0.360] | 0.075 [0.058, 0.094] | 0.820 [0.794, 0.846] | 0.000 [0.000, 0.000] |
| G2 | 0.000 [0.000, 0.000] | 0.305 [0.240, 0.370] | 0.076 [0.059, 0.096] | 0.819 [0.791, 0.845] | 0.010 [0.000, 0.025] |

Safety ASR = mean success over A1/A3/A4. PSR = A2 only. Macro = mean over all four. Acc = task accuracy on attacked cases. CIs are percentile bootstrap (n=2000).

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.545 [0.475, 0.615] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.530 [0.460, 0.600] | 0.300 [0.240, 0.365] | 0.305 [0.245, 0.370] |
| indirect_injection | 0.905 [0.860, 0.945] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.605 [0.535, 0.670] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.977 [0.960, 0.993] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| nova-pro | 0.393 [0.337, 0.450] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 5 — Input ablation (G1 only)

| Input mode | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| hybrid | 0.000 [0.000, 0.000] | 0.300 [0.235, 0.360] | 0.075 [0.058, 0.094] | 0.820 [0.794, 0.846] | 0.000 [0.000, 0.000] |
| rules | 0.000 [0.000, 0.000] | 0.415 [0.345, 0.480] | 0.104 [0.084, 0.125] | 0.786 [0.757, 0.814] | 0.000 [0.000, 0.000] |
| llm | 0.457 [0.417, 0.497] | 0.335 [0.270, 0.405] | 0.426 [0.391, 0.461] | 0.393 [0.359, 0.426] | 0.000 [0.000, 0.000] |

G0 rows for rules/llm ablations are borrowed from main. Hybrid = rules first, then LLM residual. This ablation is the primary composition result: rules drive known instruction/safety templates; hybrid slightly improves PSR; LLM-only is weak.

### LLM-only G1/G2 (for G2 rescue contrast)

| Guardrail | Safety ASR | PSR | Acc | Over-refusal |
|---|---:|---:|---:|---:|
| G0 | 0.685 [0.648, 0.723] | 0.530 [0.460, 0.600] | 0.279 [0.249, 0.310] | 0.000 [0.000, 0.000] |
| G1 | 0.457 [0.417, 0.497] | 0.335 [0.270, 0.405] | 0.393 [0.359, 0.426] | 0.000 [0.000, 0.000] |
| G2 | 0.007 [0.002, 0.013] | 0.355 [0.290, 0.420] | 0.389 [0.354, 0.424] | 0.015 [0.000, 0.035] |

On LLM-only, G2 still cuts Safety ASR (0.457 → 0.007). Defense-in-depth matters when input is weak.

### Rules-only G1/G2

| Guardrail | Safety ASR | PSR | Acc | Over-refusal |
|---|---:|---:|---:|---:|
| G0 | 0.685 [0.648, 0.723] | 0.530 [0.460, 0.600] | 0.279 [0.249, 0.310] | 0.000 [0.000, 0.000] |
| G1 | 0.000 [0.000, 0.000] | 0.415 [0.345, 0.480] | 0.786 [0.757, 0.814] | 0.000 [0.000, 0.000] |
| G2 | 0.000 [0.000, 0.000] | 0.430 [0.360, 0.500] | 0.787 [0.757, 0.815] | 0.015 [0.000, 0.035] |

## Figure data — Safety ASR vs benign accuracy

| Guardrail | Safety ASR | Benign Acc | Attack Acc | Over-refusal |
|---|---:|---:|---:|---:|
| G0 | 0.685 | 0.875 | 0.279 | 0.000 |
| G1 | 0.000 | 0.865 | 0.820 | 0.000 |
| G2 | 0.000 | 0.870 | 0.819 | 0.010 |

Hybrid G1 does **not** trade benign accuracy for safety (benign Acc 0.875 → 0.865; over-refusal 0.000).

## Mechanism (main hybrid)

- G1 decisions on attacks: `{'sanitize': 717, 'allow': 77, 'block': 6}`
- G1 by attack: `{'authority_conflict': {'sanitize': 200}, 'context_poisoning': {'allow': 77, 'block': 6, 'sanitize': 117}, 'indirect_injection': {'sanitize': 200}, 'policy_retrieval': {'sanitize': 200}}`
- G2 output: `{'pass': 759, 'missing': 4, 'rewrite': 11, 'block': 26}`
- Rescue: G0 successes=517/800; G1 stopped 462; G2 after G1 miss 10
- G2-correct via: `{'pass': 644, 'rewrite': 11}` (rewrite=11)

A1/A3/A4 are fully sanitized by rules. Residual `allow` is almost only A2 poisoning.

## Experiment 4 — Unseen attack transfer

Defense was frozen before evaluating attacks generated from unseen templates and a different generator (`deepseek`; 149/150 spans LLM-rewritten). A2 is excluded (integrity leftover, not an instruction-template match concern). Clean utility is not re-run.

Transfer conditions: 900 (attack=900).

| Guardrail | Safety ASR ↓ | Acc ↑ |
|---|---:|---:|
| G0 | 0.113 [0.080, 0.150] | 0.827 [0.783, 0.870] |
| G1 | 0.093 [0.063, 0.127] | 0.830 [0.787, 0.873] |
| G2 | 0.000 [0.000, 0.000] | 0.793 [0.747, 0.837] |

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.190 [0.120, 0.270] | 0.190 [0.120, 0.270] | 0.000 [0.000, 0.000] |
| indirect_injection | 0.150 [0.080, 0.220] | 0.090 [0.040, 0.150] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.133 [0.080, 0.187] | 0.113 [0.067, 0.167] | 0.000 [0.000, 0.000] |
| nova-pro | 0.093 [0.047, 0.147] | 0.073 [0.033, 0.120] | 0.000 [0.000, 0.000] |

- Transfer G1 decisions: `{'allow': 249, 'sanitize': 40, 'block': 11}`
- Transfer G1 by attack: `{'authority_conflict': {'allow': 98, 'block': 1, 'sanitize': 1}, 'indirect_injection': {'allow': 79, 'sanitize': 13, 'block': 8}, 'policy_retrieval': {'allow': 72, 'sanitize': 26, 'block': 2}}`

A rise from 0% in-distribution ASR to a small held-out ASR is expected and more credible than a second 0%: deterministic filters are strong on known structures; robustness can degrade under unseen formulations.

## Caveats

- Counts are **experimental conditions**, not LLM API calls.
- A2 success is an integrity metric (PSR), not Safety ASR. We do not add poisoning-specific rules to force PSR → 0.
- Attack acceptance never uses G0 effectiveness (no selection bias).
- In-distribution hybrid rules match known operator templates; Experiment 4 tests unseen phrasing with the defense frozen.
