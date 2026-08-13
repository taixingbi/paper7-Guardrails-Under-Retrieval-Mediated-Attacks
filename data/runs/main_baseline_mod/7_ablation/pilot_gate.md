# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'allow': 228, 'block': 141, 'sanitize': 31}`
- G2 output decisions on attacks: `{'block': 147, 'pass': 120, 'missing': 133}`
- G2 input→output: `{'allow->block': 147, 'block->?': 133, 'allow->pass': 92, 'sanitize->pass': 28}`
- Rescue: G0 successes=260/400; G1 stopped 104; G2 rescued after G1 miss 112
- G2 correct by output decision: `{'pass': 89}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 weak**: 228/400 (57.0%) attacked contexts were `allow` — input rarely intervenes.
2. **G2 mechanism**: block=147, rewrite=0, pass=120. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
