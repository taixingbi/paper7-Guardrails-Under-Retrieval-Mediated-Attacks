# Frozen defense (GURMA main)

Locked after pilot_v3 gate review. **Do not edit prompts or hybrid flag once main starts.**

| Knob | Value |
|------|--------|
| `guardrail_prompt_version` | `v3` |
| `input_hybrid` | `true` (rules first, LLM residual) |
| Input prompt | `prompts/guardrails/input_v3.txt` |
| Output prompt | `prompts/guardrails/output_v3.txt` |
| Rules | `src/gurma/guardrails/rules.py` |
| Answer models | `nova-pro`, `llama` |
| Guard/judge model | `gpt-oss` |
| Clean freeze | `both` models correct |
| Attack accept | `semantic_valid AND payload_present` |

Pilot evidence: G1 Safety ASR 0.717→0.000; 147/160 sanitize; over-refusal ~0.

Main command:

```bash
gurma -c configs/main.yaml run
```

Expected experimental conditions: `100×4×3×2 + 100×3×2 = 3000` (API calls ≫ 3000).

## Input ablations (same frozen seeds/attacks)

```bash
# rules-only input (G1/G2 only; G0 merged from main)
gurma -c configs/main_ablation_rules.yaml rerun-guardrails

# LLM-only input
gurma -c configs/main_ablation_llm.yaml rerun-guardrails

# Compare G1 across hybrid / rules / llm
gurma ablation-report

# Paper-facing tables
gurma report
```

## Experiment 4 — unseen attack transfer

Defense stays frozen. New attacks use held-out templates + `deepseek` rewrites.

```bash
gurma -c configs/main_transfer.yaml run-transfer
gurma report
```

Expected conditions: `50 seeds × 3 attacks × 3 guardrails × 2 models = 900` (no clean re-run).

## Experiment 5 — placement (Q / C / O / CO)

Defense stays frozen. Same hybrid v3; only *where* it is applied changes.
Reuses main seeds/attacks (`seed_limit: 50`).

| ID | Surface |
|----|---------|
| Q | Query / user turn only |
| C | Retrieved context only (≈ G1) |
| O | Model output only |
| CO | Context + output (≈ G2) |

```bash
gurma -c configs/main_placement.yaml rerun-guardrails
gurma report
```

Expected conditions: `50 × 4 attacks × 4 placements × 2 models = 1600` (no clean re-run).

## Stronger paper experiments (P0–P2)

Defense freeze still applies. Prefer these over expanding HotpotQA seed count.

```bash
# External baselines (classic PI detector / LLM moderation)
gurma -c configs/main_baseline_pi.yaml rerun-guardrails
gurma -c configs/main_baseline_mod.yaml rerun-guardrails
gurma baseline-compare

# Guardrail model-size ablation (Ministral 3B/8B/14B vs gpt-oss)
gurma -c configs/main_guard_ministral_3b.yaml rerun-guardrails
gurma -c configs/main_guard_ministral_8b.yaml rerun-guardrails
gurma -c configs/main_guard_ministral_14b.yaml rerun-guardrails
gurma guard-size-compare

# Guard-size × unseen (reuse Exp-4 held-out attacks; G1)
for cfg in main_xfer_llm_s main_xfer_llm_m main_xfer_llm_l \
           main_xfer_hybrid_s main_xfer_hybrid_m main_xfer_hybrid_l; do
  gurma -c configs/${cfg}.yaml rerun-guardrails
done
gurma xfer-size-compare

# Experiment 6 — Guard model capacity (S/M/L × LLM-only|hybrid; Nova Pro; G1)
for cfg in main_e6_llm_s main_e6_llm_m main_e6_llm_l \
           main_e6_hybrid_s main_e6_hybrid_m main_e6_hybrid_l; do
  gurma -c configs/${cfg}.yaml rerun-guardrails
done
gurma capacity-compare

# Adaptive attacker (knows rule triggers)
gurma -c configs/main_adaptive.yaml run-transfer

# Cross-dataset (SQuAD; freeze HotpotQA defense)
gurma -c configs/main_squad.yaml run

# Third target model
gurma -c configs/main_third_model.yaml rerun-guardrails
```

Latency / LLM-call overhead is recorded in `RunRecord.metadata` and `6_metrics` cost tables.