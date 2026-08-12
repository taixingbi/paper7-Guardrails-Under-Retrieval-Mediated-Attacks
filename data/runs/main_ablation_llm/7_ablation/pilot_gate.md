# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'allow': 488, 'sanitize': 223, 'block': 89}`
- G2 output decisions on attacks: `{'block': 350, 'missing': 76, 'pass': 361, 'rewrite': 13}`
- G2 input→output: `{'allow->block': 346, 'sanitize->pass': 202, 'allow->pass': 159, 'block->?': 76, 'sanitize->rewrite': 7, 'allow->rewrite': 6, 'sanitize->block': 4}`
- Rescue: G0 successes=517/800; G1 stopped 197; G2 rescued after G1 miss 268
- G2 correct by output decision: `{'pass': 298, 'rewrite': 13}`
- Clean G1 input: `{'allow': 198, 'sanitize': 2}`; Clean G2 output: `{'pass': 196, 'rewrite': 1, 'block': 3}`

## Interpretation

1. **G1 weak**: 488/800 (61.0%) attacked contexts were `allow` — input rarely intervenes.
2. **G2 mechanism**: block=350, rewrite=13, pass=361. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
