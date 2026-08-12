# paper7-Guardrails-Under-Retrieval-Mediated-Attacks

**GURMA** — Guardrails Under Retrieval-Mediated Attacks.

Evaluate input / defense-in-depth guardrails against retrieval-mediated attacks on HotpotQA-style RAG answering.

## Locked design

| Item | Choice |
|------|--------|
| Answer models | `nova-pro` (LLM-A), `llama` (LLM-B) via Bedrock marketplace |
| Guard / judge | `gpt-oss`; **input = hybrid rules + LLM** (`input_hybrid: true`) |
| Prompt version | **`v3` frozen for main** (see [FREEZE.md](FREEZE.md)) |
| Scale | smoke → 20-seed pilot → **100-seed main** |
| Clean freeze | both models must answer correctly (`clean_pass_mode: both`) |
| Attack accept | `semantic_valid AND payload_present` only |
| G0 effect | annotation only — **not** an acceptance gate |

## Experimental conditions vs API calls

Pilot **experimental conditions**:

- Adversarial: `20 × 4 × 3 × 2 = 480`
- Clean control: `20 × 3 × 2 = 120`
- **Total = 600 conditions**

Inference / API calls are **substantially more** than 600 (P2 dual-model clean validation, attack generation, P4 G0 effect annotation, G1 input guard, G2 input+output guard, judges). Do not equate “600 runs” with “600 LLM calls”.

## Setup

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
# Set GURMA_INFERENCE_URL from example.md (Bedrock Function URL)
```

## Run

Offline smoke (fixtures + heuristics, no API):

```bash
gurma -c configs/smoke.yaml run --skip-llm
```

20-seed pilot (requires `.env` + HotpotQA download):

```bash
gurma -c configs/pilot.yaml run
```

Recompute tables only:

```bash
gurma -c configs/pilot.yaml rebuild-report
```

Main (**v3 frozen** — see [FREEZE.md](FREEZE.md); 3000 experimental conditions):

```bash
gurma -c configs/main.yaml run
```

## Pipeline stages

| Stage | Output |
|-------|--------|
| P1 | `data/runs/<id>/1_seeds/clean_seeds.jsonl` |
| P2 | `2_validated_seeds/validated_seeds.jsonl` (frozen) |
| P3 | `3_attacks/attacks.jsonl` |
| P4 | `4_validated_attacks/validated_attacks.jsonl` |
| P5 | `5_runs/run_records.jsonl` |
| P6 | `6_metrics/metrics.json` + `metrics.md` |

## Paper report

```bash
gurma paper-report
```

Writes [reports/paper7_results.md](reports/paper7_results.md) from saved `metrics.json` (no LLM).

## Experiment 4 — unseen attack transfer

Defense stays frozen. Held-out templates + `deepseek` generator; no clean re-run.

```bash
gurma -c configs/main_transfer.yaml run-transfer
gurma paper-report
```

50 seeds × A1/A3/A4 × G0/G1/G2 × 2 models = 900 conditions.

## Metrics

- **Instruction/Safety ASR** — A1, A3, A4 (lower better)
- **Poisoning Success Rate (PSR)** — A2 only (lower better)
- **Macro attack success** — mean over all four
- **Task Accuracy**, **Over-refusal** (clean), **Safety Violation Rate**

Per-attack success functions are type-specific (injection follow / adopt poison / safety violation / authority follow).

## Guardrail prompt freeze

Prompts live in `prompts/guardrails/{input,output}_v1.txt`.

Each run stores `guardrail_prompt_version`, `guardrail_model`, `guardrail_raw_output`, `parsed_decision`, `sanitized_text`.

Pilot may iterate prompts; **once main starts, do not change** `guardrail_prompt_version`.

## Pilot gate (after pilot run)

```bash
gurma -c configs/pilot.yaml pilot-gate
```

Writes `data/runs/pilot/7_ablation/pilot_gate.md` with G1/G2 decision distributions and rescue counts.

## Iterate guardrail prompts (keep seeds/attacks frozen)

```bash
# v2: stronger LLM prompts only
gurma -c configs/pilot_v2.yaml rerun-guardrails

# v3: hybrid input (rules first + LLM residual) + strict output
gurma -c configs/pilot_v3.yaml rerun-guardrails
```

Compare under `data/runs/pilot/` (v1) vs `pilot_v2/` vs `pilot_v3/`. Freeze prompts before main.

## Out of scope until pilot story holds

No real retriever, no full corpus poisoning pipeline, no extra answer LLMs, no extra guardrail vendors.
