# Guard-size × unseen attacks (G1)

Guard-size × unseen (held-out) attacks. Same 50 seeds and A1/A3/A4 templates as Experiment 4. G1 only. Rules mostly miss (~83% allow), so residual / LLM-only guard size can actually move Safety ASR. gpt-oss hybrid is the existing Exp-4 G1 row (n=300), not re-inferred.

| Mode | Size | Guard LLM | Safety ASR | Acc | mean ms | LLM calls | n |
|---|---|---|---:|---:|---:|---:|---:|
| llm | S | ministral-3b (~3B) | 0.060 [0.033, 0.087] | 0.513 [0.457, 0.567] | 1310.0 | 1.70 | 300 |
| llm | M | ministral-14b (~14B) | 0.083 [0.053, 0.113] | 0.577 [0.520, 0.630] | 1701.5 | 1.69 | 300 |
| llm | L | llama (~70B) | 0.107 [0.077, 0.143] | 0.617 [0.563, 0.670] | 1739.2 | 1.75 | 300 |
| hybrid | S | ministral-3b (~3B) | 0.047 [0.023, 0.070] | 0.540 [0.483, 0.597] | 1722.4 | 1.10 | 300 |
| hybrid | M | ministral-14b (~14B) | 0.100 [0.067, 0.137] | 0.560 [0.503, 0.617] | 1803.2 | 1.37 | 300 |
| hybrid | L | llama (~70B) | 0.103 [0.073, 0.140] | 0.623 [0.570, 0.677] | 1670.9 | 1.50 | 300 |
| hybrid | 120B | gpt-oss (~120B, Exp 4) | 0.093 [0.063, 0.127] | 0.830 [0.787, 0.873] | — | — | 300 |

## Safety ASR by mode × size

| Mode | S (3B) | M (14B) | L (70B) | gpt-oss (120B) |
|---|---:|---:|---:|---:|
| llm | 0.060 [0.033, 0.087] | 0.083 [0.053, 0.113] | 0.107 [0.077, 0.143] | — |
| hybrid | 0.047 [0.023, 0.070] | 0.100 [0.067, 0.137] | 0.103 [0.073, 0.140] | 0.093 [0.063, 0.127] |
