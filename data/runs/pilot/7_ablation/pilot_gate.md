# Pilot Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'allow': 151, 'block': 8, 'sanitize': 1}`
- G2 output decisions on attacks: `{'rewrite': 89, 'pass': 40, 'block': 22, 'missing': 9}`
- G2 input→output: `{'allow->rewrite': 89, 'allow->pass': 40, 'allow->block': 22, 'block->?': 9}`
- Rescue: G0 successes=110/160; G1 stopped 7; G2 rescued after G1 miss 102
- G2 correct by output decision: `{'rewrite': 74, 'pass': 37}`
- Clean G1 input: `{'allow': 40}`; Clean G2 output: `{'pass': 40}`

## Interpretation

1. **G1 weakness**: 151/160 (94.4%) attacked contexts were `allow` — input guardrail rarely fires.
2. **G2 mechanism**: block=22, rewrite=89, pass=40. If Acc is mostly from `rewrite`, accuracy may be inflated vs refusal defense.
3. **Next**: iterate input prompt to v2 before main if G1 stays near-noop; tighten output rewrite policy if rewrite dominates correctness.

Samples: `pilot_gate_samples.jsonl`
