# Gate Review

## Verdict signals

- G1 input decisions on attacks: `{'allow': 202, 'block': 94, 'sanitize': 4}`
- G2 output decisions on attacks: `{}`
- G2 input→output: `{}`
- Rescue: G0 successes=0/0; G1 stopped 0; G2 rescued after G1 miss 0
- G2 correct by output decision: `{}`
- Clean G1 input: `{}`; Clean G2 output: `{}`

## Interpretation

1. **G1 weak**: 202/300 (67.3%) attacked contexts were `allow` — input rarely intervenes.
2. **G2 mechanism**: block=0, rewrite=0, pass=0. Rewrite is rare — Acc gains are not primarily rewrite-inflated.
3. Compare against ablations (rules-only / LLM-only / hybrid) before claiming which input component drives Safety ASR reductions.

Samples: `pilot_gate_samples.jsonl`
