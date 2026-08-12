# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 717, 'allow': 77, 'block': 6}`
- G2 output decisions on attacks: `{'pass': 759, 'missing': 4, 'rewrite': 11, 'block': 26}`
- G2 input→output: `{'sanitize->pass': 692, 'allow->pass': 67, 'allow->block': 19, 'sanitize->rewrite': 10, 'sanitize->block': 7, 'block->?': 4, 'allow->rewrite': 1}`
- Rescue: G0 successes=517/800; G1 stopped 462; G2 rescued after G1 miss 10
- G2 correct by output decision: `{'pass': 644, 'rewrite': 11}`
- Clean G1 input: `{'allow': 196, 'sanitize': 4}`; Clean G2 output: `{'pass': 196, 'rewrite': 2, 'block': 2}`

## Interpretation

1. **G1 active**: 723/800 (90.4%) attacked contexts were sanitize/block; allow=77 (9.6%).
2. **G2 mechanism**: block=26, rewrite=11, pass=759. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
