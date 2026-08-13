# Defense Comparison (G1)

G1-only comparison across GURMA input modes and external baselines. pi_detector / moderation are not GURMA template rules. Baseline runs may use seed_limit=50; check n_attack.

| Defense | Safety ASR | PSR | Acc | mean ms | LLM calls | n |
|---|---:|---:|---:|---:|---:|---:|
| hybrid | 0.000 [0.000, 0.000] | 0.300 [0.235, 0.360] | 0.820 [0.794, 0.846] | — | — | 800 |
| rules | 0.000 [0.000, 0.000] | 0.415 [0.345, 0.480] | 0.786 [0.757, 0.814] | — | — | 800 |
| llm | 0.457 [0.417, 0.497] | 0.335 [0.270, 0.405] | 0.393 [0.359, 0.426] | — | — | 800 |
| pi_detector | 0.403 [0.353, 0.463] | 0.550 [0.450, 0.650] | 0.470 [0.422, 0.520] | 1138.0 | 1.00 | 400 |
| moderation | 0.377 [0.320, 0.433] | 0.480 [0.380, 0.580] | 0.225 [0.185, 0.268] | 4461.1 | 1.65 | 400 |
