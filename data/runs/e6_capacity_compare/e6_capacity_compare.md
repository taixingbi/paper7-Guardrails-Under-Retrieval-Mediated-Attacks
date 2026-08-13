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
