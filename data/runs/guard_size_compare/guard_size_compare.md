# Guardrail model-size ablation (G1, hybrid v3)

Frozen hybrid v3; only the guardrail LLM changes. Ministral 3B/8B/14B are a size ladder; gpt-oss is the main 120B reference (full main n may differ from seed_limit=50 Ministral runs). Rules fire first — expect limited Safety ASR movement in-distribution.

| Guard LLM | Safety ASR | PSR | Acc | mean ms | LLM calls | n |
|---|---:|---:|---:|---:|---:|---:|
| ministral-3b | 0.000 [0.000, 0.000] | 0.340 [0.250, 0.430] | 0.848 [0.810, 0.882] | 8535.0 | 1.08 | 400 |
| ministral-8b | 0.000 [0.000, 0.000] | 0.410 [0.320, 0.510] | 0.828 [0.790, 0.860] | 9973.4 | 0.98 | 400 |
| ministral-14b | 0.000 [0.000, 0.000] | 0.580 [0.480, 0.670] | 0.780 [0.740, 0.818] | 9396.6 | 0.98 | 400 |
| gpt-oss (120B, main) | 0.000 [0.000, 0.000] | 0.300 [0.235, 0.360] | 0.820 [0.794, 0.846] | — | — | 800 |
