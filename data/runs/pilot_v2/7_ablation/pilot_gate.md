# Pilot Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'allow': 153, 'sanitize': 6, 'block': 1}`
- G2 output decisions on attacks: `{'block': 101, 'pass': 56, 'rewrite': 1, 'missing': 2}`
- G2 input→output: `{'allow->block': 101, 'allow->pass': 46, 'sanitize->pass': 10, 'block->?': 2, 'allow->rewrite': 1}`
- Rescue: G0 successes=110/160; G1 stopped 4; G2 rescued after G1 miss 82
- G2 correct by output decision: `{'pass': 43, 'rewrite': 1}`
- Clean G1 input: `{'allow': 40}`; Clean G2 output: `{'pass': 39, 'rewrite': 1}`

## Interpretation

1. **G1 weakness**: 153/160 (95.6%) attacked contexts were `allow` — input guardrail rarely fires.
2. **G2 mechanism**: block=101, rewrite=1, pass=56. If Acc is mostly from `rewrite`, accuracy may be inflated vs refusal defense.
3. **Next**: iterate input prompt to v2 before main if G1 stays near-noop; tighten output rewrite policy if rewrite dominates correctness.

Samples: `pilot_gate_samples.jsonl`
