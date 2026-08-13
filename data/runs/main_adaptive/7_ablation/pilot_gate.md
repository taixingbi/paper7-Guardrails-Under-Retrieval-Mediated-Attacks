# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'allow': 267, 'block': 13, 'sanitize': 20}`
- G2 output decisions on attacks: `{'missing': 15, 'pass': 188, 'block': 96, 'rewrite': 1}`
- G2 input→output: `{'allow->pass': 163, 'allow->block': 96, 'sanitize->pass': 25, 'block->?': 15, 'allow->rewrite': 1}`
- Rescue: G0 successes=103/300; G1 stopped 8; G2 rescued after G1 miss 95
- G2 correct by output decision: `{'pass': 173, 'rewrite': 1}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 weak**: 267/300 (89.0%) attacked contexts were `allow` — input rarely intervenes.
2. **G2 mechanism**: block=96, rewrite=1, pass=188. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
