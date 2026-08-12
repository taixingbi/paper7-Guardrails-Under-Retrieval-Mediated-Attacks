# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'allow': 249, 'sanitize': 40, 'block': 11}`
- G2 output decisions on attacks: `{'block': 31, 'pass': 258, 'missing': 11}`
- G2 input→output: `{'allow->pass': 226, 'sanitize->pass': 32, 'allow->block': 31, 'block->?': 11}`
- Rescue: G0 successes=34/300; G1 stopped 9; G2 rescued after G1 miss 25
- G2 correct by output decision: `{'pass': 238}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 weak**: 249/300 (83.0%) attacked contexts were `allow` — input rarely intervenes.
2. **G2 mechanism**: block=31, rewrite=0, pass=258. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
