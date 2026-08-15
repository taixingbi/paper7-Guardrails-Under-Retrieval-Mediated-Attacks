# Defense Comparison (G1)

G1-only comparison on the **same 50 freeze seeds** (n_attack=400 = 50×4 attacks×2 models). hybrid/rules/llm are subsets of the 100-seed runs; pi_detector / moderation were already seed_limit=50. pi_detector / moderation are not GURMA template rules.

| Defense | Safety ASR | PSR | Acc | mean ms | LLM calls | n |
|---|---:|---:|---:|---:|---:|---:|
| hybrid | 0.000 [0.000, 0.000] | 0.310 [0.220, 0.400] | 0.850 [0.815, 0.882] | — | — | 400 |
| rules | 0.000 [0.000, 0.000] | 0.400 [0.310, 0.490] | 0.825 [0.787, 0.860] | — | — | 400 |
| llm | 0.440 [0.383, 0.493] | 0.320 [0.230, 0.420] | 0.427 [0.383, 0.480] | — | — | 400 |
| pi_detector | 0.403 [0.353, 0.463] | 0.550 [0.450, 0.650] | 0.470 [0.422, 0.520] | 1138.0 | 1.00 | 400 |
| moderation | 0.377 [0.320, 0.433] | 0.480 [0.380, 0.580] | 0.225 [0.185, 0.268] | 4461.1 | 1.65 | 400 |
