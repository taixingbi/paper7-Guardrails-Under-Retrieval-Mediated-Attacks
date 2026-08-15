# Guardrail model-size ablation (G1, hybrid v3)

Frozen hybrid v3; only the guardrail LLM changes. Ministral 3B/8B/14B vs gpt-oss 120B on the **same 50 freeze seeds** (first 50 of main; n_attack=400 = 50×4 attacks×2 models). gpt-oss numbers are a subset of the existing main run — no re-inference. Rules fire first — expect limited Safety ASR movement in-distribution.

| Guard LLM | Safety ASR | PSR | Acc | mean ms | LLM calls | n |
|---|---:|---:|---:|---:|---:|---:|
| ministral-3b | 0.000 [0.000, 0.000] | 0.340 [0.250, 0.430] | 0.848 [0.810, 0.882] | 8535.0 | 1.08 | 400 |
| ministral-8b | 0.000 [0.000, 0.000] | 0.410 [0.320, 0.510] | 0.828 [0.790, 0.860] | 9973.4 | 0.98 | 400 |
| ministral-14b | 0.000 [0.000, 0.000] | 0.580 [0.480, 0.670] | 0.780 [0.740, 0.818] | 9396.6 | 0.98 | 400 |
| gpt-oss (120B, matched 50) | 0.000 [0.000, 0.000] | 0.310 [0.220, 0.400] | 0.850 [0.815, 0.882] | — | — | 400 |
