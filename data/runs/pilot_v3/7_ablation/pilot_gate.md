# Pilot Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'sanitize': 147, 'allow': 13}`
- G2 output decisions on attacks: `{'pass': 152, 'block': 6, 'rewrite': 2}`
- G2 input→output: `{'sanitize->pass': 142, 'allow->pass': 10, 'allow->block': 6, 'sanitize->rewrite': 2}`
- Rescue: G0 successes=111/160; G1 stopped 104; G2 rescued after G1 miss 1
- G2 correct by output decision: `{'pass': 133, 'rewrite': 2}`
- Clean G1 input: `{'allow': 39, 'sanitize': 1}`; Clean G2 output: `{'pass': 39, 'rewrite': 1}`

## Interpretation

1. **G1 weakness**: 13/160 (8.1%) attacked contexts were `allow` — input guardrail rarely fires.
2. **G2 mechanism**: block=6, rewrite=2, pass=152. If Acc is mostly from `rewrite`, accuracy may be inflated vs refusal defense.
3. **Next**: iterate input prompt to v2 before main if G1 stays near-noop; tighten output rewrite policy if rewrite dominates correctness.

Samples: `pilot_gate_samples.jsonl`
