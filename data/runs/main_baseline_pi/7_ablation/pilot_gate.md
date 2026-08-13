# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 100, 'allow': 300}`
- G2 output decisions on attacks: `{'pass': 227, 'block': 166, 'rewrite': 7}`
- G2 input→output: `{'allow->block': 166, 'allow->pass': 128, 'sanitize->pass': 99, 'allow->rewrite': 6, 'sanitize->rewrite': 1}`
- Rescue: G0 successes=260/400; G1 stopped 99; G2 rescued after G1 miss 108
- G2 correct by output decision: `{'pass': 183, 'rewrite': 7}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 weak**: 300/400 (75.0%) attacked contexts were `allow` — input rarely intervenes.
2. **G2 mechanism**: block=166, rewrite=7, pass=227. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
