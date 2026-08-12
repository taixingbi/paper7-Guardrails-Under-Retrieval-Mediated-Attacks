# Input Guardrail Ablation (G1)

G0 borrowed from main for rules/llm ablations. Compare G1 to isolate input-component contribution.

| Input mode | Safety ASR | PSR | Macro | Acc | Over-refusal |
|---|---:|---:|---:|---:|---:|
| hybrid | 0.000 | 0.300 | 0.075 | 0.820 | 0.000 |
| rules | 0.000 | 0.415 | 0.104 | 0.786 | 0.000 |
| llm | 0.457 | 0.335 | 0.426 | 0.393 | 0.000 |
