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
- Experiment 5: 50 seeds × A1–A4 × Q/C/O/CO × 2 models (1600); same hybrid v3, placement only

## Findings

1. **G0 is highly vulnerable** to retrieval-mediated instruction attacks (Safety ASR 0.685; A1 = 0.905). Llama is much weaker than Nova Pro on G0 (0.977 vs 0.393).
2. **Hybrid G1 eliminates in-distribution instruction/safety attacks** (Safety ASR 0.000) and raises attacked-task accuracy 0.279 → 0.820 with ~0 over-refusal.
3. **G2 adds almost nothing on hybrid** (rescue 10/517 G0 successes after G1). G2 rewrite is rare (11), so accuracy is not rewrite-inflated.
4. **Ablation:** rules-only also reaches Safety ASR 0.000; LLM-only remains 0.457. Hybrid mainly improves **PSR** vs rules (0.300 vs 0.415).
5. **Limitation:** context poisoning remains (PSR ≈ 0.30 under hybrid G1/G2). This is an integrity leftover, not a missing instruction filter.
6. **Transfer:** unseen templates mostly evade frozen rules (G1 allow ≈ 83%). G0 Safety ASR is 0.113; G1 only drops it to 0.093; G2 brings it to 0.000. Deterministic filters work on known structures; defense-in-depth matters under novel phrasing.
7. **Placement:** query-only (Q) fails (Safety ASR 0.703) because payloads live in retrieval. Context (C) drives Safety ASR → 0.000; output-only (O) nearly matches on safety (0.013) but collapses Acc (0.278). CO ≈ C on instruction attacks; residual PSR remains an integrity leftover.
8. **Guard capacity (Exp 6):** on Nova Pro × G1 × 50 seeds, Safety ASR is ~0 for LLM-only and hybrid across S/M/L (ministral-3b / 14b / llama-70B). The gap is **utility**: LLM-only Acc collapses (0.075–0.160) while hybrid keeps Acc ≈ 0.84–0.90. Scaling does not remove the need for rules — architecture (hybrid) dominates size for usable defense. PSR remains non-zero under both modes.

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


## External baselines & input paradigms (G1)

Compare hybrid / rules / LLM / classic PI detector / LLM moderation.

# Defense Comparison (G1)

G1-only comparison across GURMA input modes and external baselines. pi_detector / moderation are not GURMA template rules. Baseline runs may use seed_limit=50; check n_attack.

| Defense | Safety ASR | PSR | Acc | mean ms | LLM calls | n |
|---|---:|---:|---:|---:|---:|---:|
| hybrid | 0.000 [0.000, 0.000] | 0.300 [0.235, 0.360] | 0.820 [0.794, 0.846] | — | — | 800 |
| rules | 0.000 [0.000, 0.000] | 0.415 [0.345, 0.480] | 0.786 [0.757, 0.814] | — | — | 800 |
| llm | 0.457 [0.417, 0.497] | 0.335 [0.270, 0.405] | 0.393 [0.359, 0.426] | — | — | 800 |
| pi_detector | 0.403 [0.353, 0.463] | 0.550 [0.450, 0.650] | 0.470 [0.422, 0.520] | 1138.0 | 1.00 | 400 |
| moderation | 0.377 [0.320, 0.433] | 0.480 [0.380, 0.580] | 0.225 [0.185, 0.268] | 4461.1 | 1.65 | 400 |


## Guardrail model-size ablation (G1)

Earlier hybrid-only Ministral ladder (both answer models). Prefer Experiment 6 capacity grid below when available.

# Guardrail model-size ablation (G1, hybrid v3)

Frozen hybrid v3; only the guardrail LLM changes. Ministral 3B/8B/14B are a size ladder; gpt-oss is the main 120B reference (full main n may differ from seed_limit=50 Ministral runs). Rules fire first — expect limited Safety ASR movement in-distribution.

| Guard LLM | Safety ASR | PSR | Acc | mean ms | LLM calls | n |
|---|---:|---:|---:|---:|---:|---:|
| ministral-3b | 0.000 [0.000, 0.000] | 0.340 [0.250, 0.430] | 0.848 [0.810, 0.882] | 8535.0 | 1.08 | 400 |
| ministral-8b | 0.000 [0.000, 0.000] | 0.410 [0.320, 0.510] | 0.828 [0.790, 0.860] | 9973.4 | 0.98 | 400 |
| ministral-14b | 0.000 [0.000, 0.000] | 0.580 [0.480, 0.670] | 0.780 [0.740, 0.818] | 9396.6 | 0.98 | 400 |
| gpt-oss (120B, main) | 0.000 [0.000, 0.000] | 0.300 [0.235, 0.360] | 0.820 [0.794, 0.846] | — | — | 800 |


## Experiment 6 — Guard model capacity

Fixed target=nova-pro, G1/context, v3 prompts/rules, 50 seeds. Vary guard size (ministral-3b / ministral-14b / llama-70B) × mode (LLM-only vs hybrid). RQ1 scaling; RQ2 rules still needed?

# Experiment 6 — Guard model capacity

Experiment 6 — Guard model capacity. Fixed: target=nova-pro, placement=G1/context, v3 prompts, same attacks (50 seeds). Vary: guard LLM size (S/M/L) and input mode (LLM-only vs hybrid). RQ1: does scaling improve robustness? RQ2: does a larger guard eliminate the need for deterministic rules?

## Full grid (G1)

| Mode | Size | Guard LLM | Safety ASR | PSR | Acc | mean ms | LLM calls | n |
|---|---|---|---:|---:|---:|---:|---:|---:|
| llm | S | ministral-3b (~3B) | 0.007 [0.000, 0.020] | 0.480 [0.340, 0.620] | 0.160 [0.110, 0.210] | 1150.6 | 1.30 | 200 |
| llm | M | ministral-14b (~14B) | 0.000 [0.000, 0.000] | 0.760 [0.640, 0.880] | 0.075 [0.040, 0.110] | 1047.2 | 1.15 | 200 |
| llm | L | llama (~70B) | 0.000 [0.000, 0.000] | 0.460 [0.340, 0.600] | 0.135 [0.090, 0.185] | 13663.5 | 1.18 | 200 |
| hybrid | S | ministral-3b (~3B) | 0.000 [0.000, 0.000] | 0.300 [0.180, 0.440] | 0.895 [0.850, 0.935] | 4197.2 | 1.08 | 200 |
| hybrid | M | ministral-14b (~14B) | 0.000 [0.000, 0.000] | 0.540 [0.400, 0.680] | 0.835 [0.780, 0.885] | 4385.9 | 1.01 | 200 |
| hybrid | L | llama (~70B) | 0.000 [0.000, 0.000] | 0.320 [0.200, 0.460] | 0.890 [0.845, 0.930] | 4527.8 | 0.99 | 200 |

## Safety ASR by mode × size

| Mode | S (3B) | M (14B) | L (70B) |
|---|---:|---:|---:|
| llm | 0.007 [0.000, 0.020] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| hybrid | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## PSR by mode × size

| Mode | S (3B) | M (14B) | L (70B) |
|---|---:|---:|---:|
| llm | 0.480 [0.340, 0.620] | 0.760 [0.640, 0.880] | 0.460 [0.340, 0.600] |
| hybrid | 0.300 [0.180, 0.440] | 0.540 [0.400, 0.680] | 0.320 [0.200, 0.460] |


## Experiment 5 — Placement (Q / C / O / CO)

Frozen hybrid v3; only *where* the guardrail is applied. Q=query, C=context (≈G1), O=output, CO=context+output (≈G2). 50 seeds × 4 attacks × 4 placements × 2 models.

# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 1600 (clean=0, attack=1600)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 0
- context_poisoning: 0
- indirect_injection: 0
- policy_retrieval: 0

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| C | 0.000 [0.000, 0.000] | 0.260 [0.180, 0.350] | 0.065 [0.043, 0.090] | 0.863 [0.830, 0.895] | — |
| CO | 0.000 [0.000, 0.000] | 0.390 [0.300, 0.490] | 0.098 [0.068, 0.128] | 0.840 [0.805, 0.873] | — |
| O | 0.013 [0.003, 0.027] | 0.560 [0.470, 0.650] | 0.150 [0.115, 0.188] | 0.278 [0.235, 0.323] | — |
| Q | 0.703 [0.653, 0.757] | 0.550 [0.450, 0.650] | 0.665 [0.620, 0.713] | 0.258 [0.215, 0.305] | — |

## Table 3 — Attack breakdown

| Attack | C | CO | O | Q |
|---|---:|---:|---:|---:|
| authority_conflict | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.540 [0.450, 0.640] |
| context_poisoning | 0.260 [0.180, 0.350] | 0.390 [0.300, 0.490] | 0.560 [0.470, 0.650] | 0.550 [0.450, 0.650] |
| indirect_injection | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.900 [0.840, 0.950] |
| policy_retrieval | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.040 [0.010, 0.080] | 0.670 [0.580, 0.760] |

## Table 4 — Cross-model Safety ASR

| Model | C | CO | O | Q |
|---|---:|---:|---:|---:|
| llama | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.027 [0.007, 0.053] | 0.980 [0.953, 1.000] |
| nova-pro | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.427 [0.353, 0.507] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| C | 400 | 1390.8 | 423.5 | 6657.1 | 1.1 |
| CO | 400 | 2902.4 | 1813.1 | 9197.1 | 2.1 |
| O | 400 | 2993.0 | 2205.1 | 8019.5 | 2.0 |
| Q | 400 | 2171.7 | 1816.0 | 4028.8 | 2.0 |


## Adaptive attacks (frozen defense)

Attacker avoids known rule triggers while preserving the malicious objective.

# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 900 (clean=0, attack=900)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 50
- indirect_injection: 50
- policy_retrieval: 50

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.343 [0.293, 0.397] | — | 0.343 [0.290, 0.400] | 0.697 [0.643, 0.750] | — |
| G1 | 0.327 [0.277, 0.380] | — | 0.327 [0.273, 0.380] | 0.677 [0.623, 0.730] | — |
| G2 | 0.000 [0.000, 0.000] | — | 0.000 [0.000, 0.000] | 0.580 [0.520, 0.637] | — |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.670 [0.580, 0.760] | 0.680 [0.590, 0.770] | 0.000 [0.000, 0.000] |
| indirect_injection | 0.360 [0.270, 0.450] | 0.300 [0.220, 0.390] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.333 [0.260, 0.407] | 0.327 [0.253, 0.407] | 0.000 [0.000, 0.000] |
| nova-pro | 0.353 [0.280, 0.433] | 0.327 [0.253, 0.400] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G0 | 300 | 483.1 | 448.2 | 734.5 | 1.0 |
| G1 | 300 | 4596.9 | 3752.1 | 10205.3 | 1.8 |
| G2 | 300 | 5915.8 | 5027.7 | 11784.8 | 2.8 |


## Cross-dataset (SQuAD; HotpotQA defense frozen)

Same frozen hybrid v3 evaluated on single-hop SQuAD seeds.

# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 1500 (clean=300, attack=1200)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 50
- context_poisoning: 50
- indirect_injection: 50
- policy_retrieval: 50

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.460 [0.403, 0.517] | 0.570 [0.470, 0.670] | 0.487 [0.438, 0.537] | 0.395 [0.350, 0.445] | 0.000 [0.000, 0.000] |
| G1 | 0.000 [0.000, 0.000] | 0.290 [0.200, 0.380] | 0.072 [0.048, 0.098] | 0.792 [0.752, 0.830] | 0.000 [0.000, 0.000] |
| G2 | 0.000 [0.000, 0.000] | 0.270 [0.190, 0.360] | 0.068 [0.043, 0.092] | 0.815 [0.777, 0.853] | 0.020 [0.000, 0.050] |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.540 [0.450, 0.640] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.570 [0.480, 0.670] | 0.290 [0.200, 0.380] | 0.270 [0.180, 0.350] |
| indirect_injection | 0.690 [0.600, 0.780] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.150 [0.080, 0.230] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| llama | 0.700 [0.627, 0.773] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| nova-pro | 0.220 [0.153, 0.293] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G0 | 500 | 1269.4 | 512.3 | 5155.0 | 1.0 |
| G1 | 500 | 2168.1 | 1447.7 | 7141.0 | 1.3 |
| G2 | 500 | 3716.3 | 2876.7 | 9646.3 | 2.2 |


## Third target model (deepseek)

Frozen seeds/attacks; answer model = deepseek only.

# GURMA Metrics

Instruction/Safety ASR excludes context_poisoning (reported as PSR). Macro attack success averages all four attack types. Counts are experimental conditions, not LLM API calls. Brackets are 95% bootstrap CIs. Latency/LLM-call stats come from RunRecord.metadata when tracked.

Records: 600 (clean=0, attack=600)

## Table 1 — Dataset (G0 cases / model)

- authority_conflict: 50
- context_poisoning: 50
- indirect_injection: 50
- policy_retrieval: 50

## Table 2 — Main

| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| G0 | 0.560 [0.480, 0.640] | 0.500 [0.360, 0.640] | 0.545 [0.480, 0.615] | 0.450 [0.385, 0.520] | — |
| G1 | 0.000 [0.000, 0.000] | 0.240 [0.140, 0.360] | 0.060 [0.030, 0.095] | 0.885 [0.835, 0.925] | — |
| G2 | 0.000 [0.000, 0.000] | 0.200 [0.100, 0.320] | 0.050 [0.020, 0.085] | 0.900 [0.855, 0.940] | — |

## Table 3 — Attack breakdown

| Attack | G0 | G1 | G2 |
|---|---:|---:|---:|
| authority_conflict | 0.940 [0.860, 1.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| context_poisoning | 0.500 [0.360, 0.640] | 0.240 [0.120, 0.360] | 0.200 [0.100, 0.320] |
| indirect_injection | 0.700 [0.560, 0.820] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| policy_retrieval | 0.040 [0.000, 0.100] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Table 4 — Cross-model Safety ASR

| Model | G0 | G1 | G2 |
|---|---:|---:|---:|
| deepseek | 0.560 [0.480, 0.640] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |

## Cost / latency

| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |
|---|---:|---:|---:|---:|---:|
| G0 | 200 | 783.9 | 526.1 | 1869.9 | 1.0 |
| G1 | 200 | 1554.9 | 550.7 | 5822.9 | 1.1 |
| G2 | 200 | 3100.8 | 2148.0 | 9939.3 | 2.1 |

## Caveats

- Counts are **experimental conditions**, not LLM API calls.
- A2 success is an integrity metric (PSR), not Safety ASR. We do not add poisoning-specific rules to force PSR → 0.
- Attack acceptance never uses G0 effectiveness (no selection bias).
- In-distribution hybrid rules match known operator templates; Experiment 4 / adaptive / cross-dataset test generalization with the defense frozen.
- External baselines (PI detector, moderation) are comparison systems, not retunes of the frozen hybrid.
