# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 654, 'allow': 146}`
- G2 output decisions on attacks: `{'pass': 744, 'block': 46, 'rewrite': 10}`
- G2 input→output: `{'sanitize->pass': 639, 'allow->pass': 105, 'allow->block': 41, 'sanitize->rewrite': 10, 'sanitize->block': 5}`
- Rescue: G0 successes=517/800; G1 stopped 436; G2 rescued after G1 miss 2
- G2 correct by output decision: `{'pass': 620, 'rewrite': 10}`
- Clean G1 input: `{'allow': 200}`; Clean G2 output: `{'pass': 194, 'rewrite': 3, 'block': 3}`

## Interpretation

1. **G1 active**: 654/800 (81.8%) attacked contexts were sanitize/block; allow=146 (18.2%).
2. **G2 mechanism**: block=46, rewrite=10, pass=744. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
