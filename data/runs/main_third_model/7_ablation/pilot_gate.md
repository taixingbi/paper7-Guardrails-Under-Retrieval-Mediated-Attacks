# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 177, 'allow': 21, 'block': 2}`
- G2 output decisions on attacks: `{'pass': 193, 'block': 6, 'missing': 1}`
- G2 input→output: `{'sanitize->pass': 176, 'allow->pass': 17, 'allow->block': 6, 'block->?': 1}`
- Rescue: G0 successes=109/200; G1 stopped 99; G2 rescued after G1 miss 2
- G2 correct by output decision: `{'pass': 180}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 active**: 179/200 (89.5%) attacked contexts were sanitize/block; allow=21 (10.5%).
2. **G2 mechanism**: block=6, rewrite=0, pass=193. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
