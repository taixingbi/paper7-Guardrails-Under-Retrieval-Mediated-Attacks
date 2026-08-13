# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 369, 'allow': 31}`
- G2 output decisions on attacks: `{'pass': 350, 'block': 48, 'rewrite': 2}`
- G2 input→output: `{'sanitize->pass': 334, 'sanitize->block': 32, 'allow->pass': 16, 'allow->block': 16, 'sanitize->rewrite': 2}`
- Rescue: G0 successes=260/400; G1 stopped 233; G2 rescued after G1 miss 1
- G2 correct by output decision: `{'pass': 324}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 active**: 369/400 (92.2%) attacked contexts were sanitize/block; allow=31 (7.8%).
2. **G2 mechanism**: block=48, rewrite=2, pass=350. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
