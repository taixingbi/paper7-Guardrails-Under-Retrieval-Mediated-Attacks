# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 370, 'allow': 11, 'block': 19}`
- G2 output decisions on attacks: `{'pass': 343, 'block': 20, 'rewrite': 19, 'missing': 18}`
- G2 input→output: `{'sanitize->pass': 337, 'sanitize->rewrite': 18, 'block->?': 18, 'sanitize->block': 14, 'allow->block': 6, 'allow->pass': 6, 'allow->rewrite': 1}`
- Rescue: G0 successes=260/400; G1 stopped 231; G2 rescued after G1 miss 1
- G2 correct by output decision: `{'pass': 312, 'rewrite': 19}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 active**: 389/400 (97.2%) attacked contexts were sanitize/block; allow=11 (2.8%).
2. **G2 mechanism**: block=20, rewrite=19, pass=343. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
