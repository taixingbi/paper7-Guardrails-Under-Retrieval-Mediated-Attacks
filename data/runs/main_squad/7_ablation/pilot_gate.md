# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 364, 'allow': 32, 'block': 4}`
- G2 output decisions on attacks: `{'rewrite': 11, 'pass': 379, 'block': 5, 'missing': 5}`
- G2 input→output: `{'sanitize->pass': 353, 'allow->pass': 26, 'sanitize->rewrite': 9, 'block->?': 5, 'allow->block': 3, 'allow->rewrite': 2, 'sanitize->block': 2}`
- Rescue: G0 successes=195/400; G1 stopped 169; G2 rescued after G1 miss 5
- G2 correct by output decision: `{'rewrite': 11, 'pass': 315}`
- Clean G1 input: `{'allow': 98, 'sanitize': 2}`; Clean G2 output: `{'rewrite': 3, 'pass': 95, 'block': 2}`

## Interpretation

1. **G1 active**: 368/400 (92.0%) attacked contexts were sanitize/block; allow=32 (8.0%).
2. **G2 mechanism**: block=5, rewrite=11, pass=379. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
