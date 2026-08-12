# Paper 7 Results Report

Generated from frozen main + input ablations. Regenerate with `gurma paper-report`.

## Setup

- Seeds: 100 HotpotQA (both-model clean freeze)
- Attacks: 4 × 100 = 400 validated cases (`accepted = semantic ∧ payload`)
- Guardrails: G0 none / G1 input / G2 input+output
- Models: `nova-pro`, `llama`; guard/judge: `gpt-oss`
- Defense freeze: hybrid input (`rules` first) + `v3` prompts ([FREEZE.md](../FREEZE.md))
- Main conditions: 3000 (2400 attack + 600 clean); API calls ≫ 3000

## Findings

1. **G0 is highly vulnerable** to retrieval-mediated instruction attacks (Safety ASR 0.685; A1 = 0.905). Llama is much weaker than Nova Pro on G0 (0.977 vs 0.393).
2. **Hybrid G1 eliminates instruction/safety attacks** (Safety ASR 0.000) and raises attacked-task accuracy 0.279 → 0.820 with ~0 over-refusal.
3. **G2 adds almost nothing on hybrid** (rescue 10/517 G0 successes after G1). G2 rewrite is rare (11), so accuracy is not rewrite-inflated.
4. **Ablation:** rules-only also reaches Safety ASR 0.000; LLM-only remains 0.457. Hybrid mainly improves **PSR** vs rules (0.300 vs 0.415).
5. **Limitation:** context poisoning remains (PSR ≈ 0.30 under hybrid G1/G2).

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
| G0 | 0.685 | 0.530 | 0.646 | 0.279 | 0.000 |
| G1 | 0.000 | 0.300 | 0.075 | 0.820 | 0.000 |
| G2 | 0.000 | 0.305 | 0.076 | 0.819 | 0.010 |

Safety ASR = mean success over A1/A3/A4. PSR = A2 only. Macro = mean over all four. Acc = task accuracy on attacked cases.

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.545 | 0.000 | 0.000 |
| context_poisoning | 0.530 | 0.300 | 0.305 |
| indirect_injection | 0.905 | 0.000 | 0.000 |
| policy_retrieval | 0.605 | 0.000 | 0.000 |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.977 | 0.000 | 0.000 |
| nova-pro | 0.393 | 0.000 | 0.000 |

## Table 5 — Input ablation (G1 only)

| Input mode | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| hybrid | 0.000 | 0.300 | 0.075 | 0.820 | 0.000 |
| rules | 0.000 | 0.415 | 0.104 | 0.786 | 0.000 |
| llm | 0.457 | 0.335 | 0.426 | 0.393 | 0.000 |

G0 rows for rules/llm ablations are borrowed from main. Hybrid = rules first, then LLM residual.

### LLM-only G1/G2 (for G2 rescue contrast)

| Guardrail | Safety ASR | PSR | Acc | Over-refusal |
|---|---:|---:|---:|---:|
| G0 | 0.685 | 0.530 | 0.279 | 0.000 |
| G1 | 0.457 | 0.335 | 0.393 | 0.000 |
| G2 | 0.007 | 0.355 | 0.389 | 0.015 |

On LLM-only, G2 still cuts Safety ASR (0.457 → 0.007). Defense-in-depth matters when input is weak.

### Rules-only G1/G2

| Guardrail | Safety ASR | PSR | Acc | Over-refusal |
|---|---:|---:|---:|---:|
| G0 | 0.685 | 0.530 | 0.279 | 0.000 |
| G1 | 0.000 | 0.415 | 0.786 | 0.000 |
| G2 | 0.000 | 0.430 | 0.787 | 0.015 |

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

## Caveats

- Counts are **experimental conditions**, not LLM API calls.
- A2 success is an integrity metric (PSR), not Safety ASR.
- Attack acceptance never uses G0 effectiveness (no selection bias).
- Hybrid rules match known operator templates; transfer to novel phrasing is untested.
