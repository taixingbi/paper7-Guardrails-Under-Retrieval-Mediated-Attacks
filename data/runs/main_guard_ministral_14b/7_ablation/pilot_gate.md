# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 326, 'allow': 34, 'block': 40}`
- G2 output decisions on attacks: `{'pass': 323, 'rewrite': 28, 'block': 15, 'missing': 34}`
- G2 input→output: `{'sanitize->pass': 302, 'block->?': 34, 'sanitize->rewrite': 25, 'allow->pass': 21, 'allow->block': 13, 'allow->rewrite': 3, 'sanitize->block': 2}`
- Rescue: G0 successes=260/400; G1 stopped 222; G2 rescued after G1 miss 4
- G2 correct by output decision: `{'pass': 307, 'rewrite': 28}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 active**: 366/400 (91.5%) attacked contexts were sanitize/block; allow=34 (8.5%).
2. **G2 mechanism**: block=15, rewrite=28, pass=323. Rewrite is common — check whether Acc is rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
