# Input Guardrail Ablation (G1)

G0 borrowed from main for rules/llm ablations. Compare G1 to isolate input-component contribution.

| Input mode | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| hybrid | 0.000 [0.000, 0.000] | 0.300 [0.235, 0.360] | 0.075 [0.058, 0.094] | 0.820 [0.794, 0.846] | 0.000 [0.000, 0.000] |
| rules | 0.000 [0.000, 0.000] | 0.415 [0.345, 0.480] | 0.104 [0.084, 0.125] | 0.786 [0.757, 0.814] | 0.000 [0.000, 0.000] |
| llm | 0.457 [0.417, 0.497] | 0.335 [0.270, 0.405] | 0.426 [0.391, 0.461] | 0.393 [0.359, 0.426] | 0.000 [0.000, 0.000] |
