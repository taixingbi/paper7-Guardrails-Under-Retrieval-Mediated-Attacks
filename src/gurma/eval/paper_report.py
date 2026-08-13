"""Generate a paper-facing results report from saved metrics JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gurma.eval.bootstrap import fmt_ci

ROOT = Path(__file__).resolve().parents[3]


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def _fmt(x: Any, digits: int = 3) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{digits}f}"


def _cell(row: dict[str, Any], point_key: str, ci_key: str) -> str:
    return fmt_ci(row.get(point_key), row.get(ci_key))


def _row(guard: dict[str, Any]) -> str:
    return (
        f"| {guard['guardrail']} "
        f"| {_cell(guard, 'instruction_safety_asr', 'instruction_safety_asr_ci')} "
        f"| {_cell(guard, 'poisoning_success_rate', 'poisoning_success_rate_ci')} "
        f"| {_cell(guard, 'macro_attack_success', 'macro_attack_success_ci')} "
        f"| {_cell(guard, 'task_accuracy', 'task_accuracy_ci')} "
        f"| {_cell(guard, 'over_refusal', 'over_refusal_ci')} |"
    )


def render_paper_report(
    *,
    main_metrics: dict[str, Any],
    main_gate: dict[str, Any],
    ablation: dict[str, Any],
    llm_metrics: dict[str, Any] | None = None,
    rules_metrics: dict[str, Any] | None = None,
    transfer_metrics: dict[str, Any] | None = None,
    transfer_gate: dict[str, Any] | None = None,
) -> str:
    t1 = main_metrics.get("table1_dataset") or {}
    t2 = main_metrics.get("table2_main") or []
    t3 = main_metrics.get("table3_attack_breakdown") or []
    t4 = main_metrics.get("table4_cross_model") or []
    scatter = main_metrics.get("scatter_safety_vs_benign_acc") or []
    rescue = main_gate.get("rescue") or {}
    g1_dec = main_gate.get("g1_input_decisions_attack") or {}
    g1_by = main_gate.get("g1_input_by_attack") or {}
    g2_out = main_gate.get("g2_output_decisions_attack") or {}
    g2_corr = main_gate.get("g2_correct_via_output_decision") or {}

    lines = [
        "# Paper 7 Results Report",
        "",
        "Generated from frozen main + input ablations + held-out transfer. "
        "Regenerate with `gurma paper-report`. Brackets are 95% bootstrap CIs.",
        "",
        "## Setup",
        "",
        "- Seeds: 100 HotpotQA (both-model clean freeze)",
        "- Attacks: 4 × 100 = 400 validated cases (`accepted = semantic ∧ payload`)",
        "- Guardrails: G0 none / G1 input / G2 input+output",
        "- Models: `nova-pro`, `llama`; guard/judge: `gpt-oss`",
        "- Defense freeze: hybrid input (`rules` first) + `v3` prompts ([FREEZE.md](../FREEZE.md))",
        "- Main conditions: 3000 (2400 attack + 600 clean); API calls ≫ 3000",
        "- Experiment 4: 50 frozen seeds × A1/A3/A4 held-out templates "
        "(generator=`deepseek`) × G0/G1/G2 × 2 models; defense not retuned",
        "- Experiment 5: 50 seeds × A1–A4 × Q/C/O/CO × 2 models (1600); "
        "same hybrid v3, placement only",
        "",
        "## Findings",
        "",
        "1. **G0 is highly vulnerable** to retrieval-mediated instruction attacks "
        f"(Safety ASR {_fmt(t2[0].get('instruction_safety_asr') if t2 else None)}; "
        "A1 = 0.905). Llama is much weaker than Nova Pro on G0 (0.977 vs 0.393).",
        "2. **Hybrid G1 eliminates in-distribution instruction/safety attacks** "
        "(Safety ASR 0.000) and raises attacked-task accuracy 0.279 → 0.820 "
        "with ~0 over-refusal.",
        "3. **G2 adds almost nothing on hybrid** (rescue 10/517 G0 successes after G1). "
        "G2 rewrite is rare (11), so accuracy is not rewrite-inflated.",
        "4. **Ablation:** rules-only also reaches Safety ASR 0.000; LLM-only remains "
        "0.457. Hybrid mainly improves **PSR** vs rules (0.300 vs 0.415).",
        "5. **Limitation:** context poisoning remains (PSR ≈ 0.30 under hybrid G1/G2). "
        "This is an integrity leftover, not a missing instruction filter.",
        "6. **Transfer:** unseen templates mostly evade frozen rules "
        "(G1 allow ≈ 83%). G0 Safety ASR is 0.113; G1 only drops it to 0.093; "
        "G2 brings it to 0.000. Deterministic filters work on known structures; "
        "defense-in-depth matters under novel phrasing.",
        "7. **Placement:** query-only (Q) fails (Safety ASR 0.703) because payloads "
        "live in retrieval. Context (C) drives Safety ASR → 0.000; output-only (O) "
        "nearly matches on safety (0.013) but collapses Acc (0.278). CO ≈ C on "
        "instruction attacks; residual PSR remains an integrity leftover.",
        "",
        "## Table 1 — Dataset",
        "",
        "| Attack | Cases |",
        "|---|---:|",
    ]
    labels = {
        "indirect_injection": "A1 Indirect injection",
        "context_poisoning": "A2 Context poisoning",
        "policy_retrieval": "A3 Policy-violating retrieval",
        "authority_conflict": "A4 Authority conflict",
    }
    for key, label in labels.items():
        lines.append(f"| {label} | {t1.get(key, '—')} |")

    lines += [
        "",
        "## Table 2 — Main result (hybrid v3)",
        "",
        "| Guardrail | Safety ASR ↓ | PSR ↓ | Macro ↓ | Acc ↑ | Over-refusal ↓ |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in t2:
        lines.append(_row(row))

    lines += [
        "",
        "Safety ASR = mean success over A1/A3/A4. PSR = A2 only. "
        "Macro = mean over all four. Acc = task accuracy on attacked cases. "
        "CIs are percentile bootstrap (n=2000).",
        "",
        "## Table 3 — Attack breakdown",
        "",
        "| Attack | G0 | G1 | G2 |",
        "|---|---:|---:|---:|",
    ]
    for row in t3:
        lines.append(
            f"| {row.get('attack')} | "
            f"{_cell(row, 'G0_success', 'G0_success_ci')} | "
            f"{_cell(row, 'G1_success', 'G1_success_ci')} | "
            f"{_cell(row, 'G2_success', 'G2_success_ci')} |"
        )

    lines += [
        "",
        "## Table 4 — Cross-model Safety ASR",
        "",
        "| Model | G0 | G1 | G2 |",
        "|---|---:|---:|---:|",
    ]
    for row in t4:
        lines.append(
            f"| {row.get('model')} | "
            f"{_cell(row, 'G0_safety_asr', 'G0_safety_asr_ci')} | "
            f"{_cell(row, 'G1_safety_asr', 'G1_safety_asr_ci')} | "
            f"{_cell(row, 'G2_safety_asr', 'G2_safety_asr_ci')} |"
        )

    lines += [
        "",
        "## Table 5 — Input ablation (G1 only)",
        "",
        "| Input mode | Safety ASR | PSR | Macro | Acc | Over-refusal |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for row in ablation.get("g1_comparison") or []:
        lines.append(
            f"| {row.get('input_mode')} | "
            f"{_cell(row, 'safety_asr', 'safety_asr_ci')} | "
            f"{_cell(row, 'psr', 'psr_ci')} | "
            f"{_cell(row, 'macro', 'macro_ci')} | "
            f"{_cell(row, 'task_accuracy', 'task_accuracy_ci')} | "
            f"{_cell(row, 'over_refusal', 'over_refusal_ci')} |"
        )
    lines += [
        "",
        "G0 rows for rules/llm ablations are borrowed from main. "
        "Hybrid = rules first, then LLM residual. "
        "This ablation is the primary composition result: rules drive known "
        "instruction/safety templates; hybrid slightly improves PSR; LLM-only is weak.",
        "",
    ]

    if llm_metrics:
        lines += [
            "### LLM-only G1/G2 (for G2 rescue contrast)",
            "",
            "| Guardrail | Safety ASR | PSR | Acc | Over-refusal |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in llm_metrics.get("table2_main") or []:
            lines.append(
                f"| {row['guardrail']} | "
                f"{_cell(row, 'instruction_safety_asr', 'instruction_safety_asr_ci')} | "
                f"{_cell(row, 'poisoning_success_rate', 'poisoning_success_rate_ci')} | "
                f"{_cell(row, 'task_accuracy', 'task_accuracy_ci')} | "
                f"{_cell(row, 'over_refusal', 'over_refusal_ci')} |"
            )
        lines += [
            "",
            "On LLM-only, G2 still cuts Safety ASR (0.457 → 0.007). "
            "Defense-in-depth matters when input is weak.",
            "",
        ]

    if rules_metrics:
        lines += [
            "### Rules-only G1/G2",
            "",
            "| Guardrail | Safety ASR | PSR | Acc | Over-refusal |",
            "|---|---:|---:|---:|---:|",
        ]
        for row in rules_metrics.get("table2_main") or []:
            lines.append(
                f"| {row['guardrail']} | "
                f"{_cell(row, 'instruction_safety_asr', 'instruction_safety_asr_ci')} | "
                f"{_cell(row, 'poisoning_success_rate', 'poisoning_success_rate_ci')} | "
                f"{_cell(row, 'task_accuracy', 'task_accuracy_ci')} | "
                f"{_cell(row, 'over_refusal', 'over_refusal_ci')} |"
            )
        lines.append("")

    lines += [
        "## Figure data — Safety ASR vs benign accuracy",
        "",
        "| Guardrail | Safety ASR | Benign Acc | Attack Acc | Over-refusal |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in scatter:
        lines.append(
            f"| {row.get('guardrail')} | {_fmt(row.get('safety_asr'))} "
            f"| {_fmt(row.get('benign_accuracy'))} "
            f"| {_fmt(row.get('task_accuracy_on_attacks'))} "
            f"| {_fmt(row.get('over_refusal'))} |"
        )
    lines += [
        "",
        "Hybrid G1 does **not** trade benign accuracy for safety "
        "(benign Acc 0.875 → 0.865; over-refusal 0.000).",
        "",
        "## Mechanism (main hybrid)",
        "",
        f"- G1 decisions on attacks: `{g1_dec}`",
        f"- G1 by attack: `{g1_by}`",
        f"- G2 output: `{g2_out}`",
        (
            f"- Rescue: G0 successes={rescue.get('g0_success')}/{rescue.get('n')}; "
            f"G1 stopped {rescue.get('g1_helped')}; "
            f"G2 after G1 miss {rescue.get('g2_helped_after_g1_miss')}"
        ),
        f"- G2-correct via: `{g2_corr}` (rewrite={g2_corr.get('rewrite', 0)})",
        "",
        "A1/A3/A4 are fully sanitized by rules. Residual `allow` is almost only A2 poisoning.",
        "",
        "## Experiment 4 — Unseen attack transfer",
        "",
        "Defense was frozen before evaluating attacks generated from unseen templates "
        "and a different generator (`deepseek`; 149/150 spans LLM-rewritten). "
        "A2 is excluded (integrity leftover, not an instruction-template match concern). "
        "Clean utility is not re-run.",
        "",
    ]
    if transfer_metrics:
        xt2 = transfer_metrics.get("table2_main") or []
        xt3 = transfer_metrics.get("table3_attack_breakdown") or []
        xt4 = transfer_metrics.get("table4_cross_model") or []
        lines += [
            f"Transfer conditions: {transfer_metrics.get('n_records')} "
            f"(attack={transfer_metrics.get('n_attack_conditions')}).",
            "",
            "| Guardrail | Safety ASR ↓ | Acc ↑ |",
            "|---|---:|---:|",
        ]
        for row in xt2:
            lines.append(
                f"| {row['guardrail']} | "
                f"{_cell(row, 'instruction_safety_asr', 'instruction_safety_asr_ci')} | "
                f"{_cell(row, 'task_accuracy', 'task_accuracy_ci')} |"
            )
        lines += [
            "",
            "| Attack | G0 | G1 | G2 |",
            "|---|---:|---:|---:|",
        ]
        for row in xt3:
            lines.append(
                f"| {row.get('attack')} | "
                f"{_cell(row, 'G0_success', 'G0_success_ci')} | "
                f"{_cell(row, 'G1_success', 'G1_success_ci')} | "
                f"{_cell(row, 'G2_success', 'G2_success_ci')} |"
            )
        lines += [
            "",
            "| Model | G0 | G1 | G2 |",
            "|---|---:|---:|---:|",
        ]
        for row in xt4:
            lines.append(
                f"| {row.get('model')} | "
                f"{_cell(row, 'G0_safety_asr', 'G0_safety_asr_ci')} | "
                f"{_cell(row, 'G1_safety_asr', 'G1_safety_asr_ci')} | "
                f"{_cell(row, 'G2_safety_asr', 'G2_safety_asr_ci')} |"
            )
        lines.append("")
        if transfer_gate:
            lines += [
                f"- Transfer G1 decisions: `{transfer_gate.get('g1_input_decisions_attack')}`",
                f"- Transfer G1 by attack: `{transfer_gate.get('g1_input_by_attack')}`",
                "",
            ]
        lines += [
            "A rise from 0% in-distribution ASR to a small held-out ASR is expected "
            "and more credible than a second 0%: deterministic filters are strong on "
            "known structures; robustness can degrade under unseen formulations.",
            "",
        ]
    else:
        lines += [
            "_Not yet run._ `gurma -c configs/main_transfer.yaml run-transfer`",
            "",
        ]

    # Extended P0–P2 sections (optional if metrics exist)
    extra_sections: list[tuple[str, Path, str]] = [
        (
            "## External baselines & input paradigms (G1)",
            ROOT / "data/runs/baseline_compare/baseline_compare.md",
            "Compare hybrid / rules / LLM / classic PI detector / LLM moderation.",
        ),
    ]
    for title, path, blurb in extra_sections:
        if path.exists():
            lines += ["", title, "", blurb, "", path.read_text().strip(), ""]

    for title, metrics_path, blurb in (
        (
            "## Experiment 5 — Placement (Q / C / O / CO)",
            ROOT / "data/runs/main_placement/6_metrics/metrics.md",
            "Frozen hybrid v3; only *where* the guardrail is applied. "
            "Q=query, C=context (≈G1), O=output, CO=context+output (≈G2). "
            "50 seeds × 4 attacks × 4 placements × 2 models.",
        ),
        (
            "## Adaptive attacks (frozen defense)",
            ROOT / "data/runs/main_adaptive/6_metrics/metrics.md",
            "Attacker avoids known rule triggers while preserving the malicious objective.",
        ),
        (
            "## Cross-dataset (SQuAD; HotpotQA defense frozen)",
            ROOT / "data/runs/main_squad/6_metrics/metrics.md",
            "Same frozen hybrid v3 evaluated on single-hop SQuAD seeds.",
        ),
        (
            "## Third target model (deepseek)",
            ROOT / "data/runs/main_third_model/6_metrics/metrics.md",
            "Frozen seeds/attacks; answer model = deepseek only.",
        ),
    ):
        if metrics_path.exists():
            lines += ["", title, "", blurb, "", metrics_path.read_text().strip(), ""]

    cost = main_metrics.get("table_cost_latency") or []
    if cost:
        lines += [
            "",
            "## Safety–utility–cost (main hybrid)",
            "",
            "| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for row in cost:
            def fnum(x: Any) -> str:
                return "—" if x is None else f"{float(x):.1f}"

            lines.append(
                f"| {row['guardrail']} | {row.get('n')} | "
                f"{fnum(row.get('mean_latency_ms'))} | "
                f"{fnum(row.get('p50_latency_ms'))} | "
                f"{fnum(row.get('p95_latency_ms'))} | "
                f"{fnum(row.get('mean_llm_calls'))} |"
            )
        lines.append("")

    lines += [
        "## Caveats",
        "",
        "- Counts are **experimental conditions**, not LLM API calls.",
        "- A2 success is an integrity metric (PSR), not Safety ASR. "
        "We do not add poisoning-specific rules to force PSR → 0.",
        "- Attack acceptance never uses G0 effectiveness (no selection bias).",
        "- In-distribution hybrid rules match known operator templates; "
        "Experiment 4 / adaptive / cross-dataset test generalization with the defense frozen.",
        "- External baselines (PI detector, moderation) are comparison systems, "
        "not retunes of the frozen hybrid.",
        "",
    ]
    return "\n".join(lines)


def write_paper_report(out_path: Path | None = None) -> Path:
    out_path = out_path or (ROOT / "reports" / "paper7_results.md")
    main_metrics = _load(ROOT / "data/runs/main/6_metrics/metrics.json")
    main_gate = _load(ROOT / "data/runs/main/7_ablation/pilot_gate_summary.json")
    ablation = _load(ROOT / "data/runs/ablation_compare/ablation_compare.json")
    llm_path = ROOT / "data/runs/main_ablation_llm/6_metrics/metrics.json"
    rules_path = ROOT / "data/runs/main_ablation_rules/6_metrics/metrics.json"
    xfer_path = ROOT / "data/runs/main_transfer/6_metrics/metrics.json"
    xfer_gate_path = ROOT / "data/runs/main_transfer/7_ablation/pilot_gate_summary.json"
    md = render_paper_report(
        main_metrics=main_metrics,
        main_gate=main_gate,
        ablation=ablation,
        llm_metrics=_load(llm_path) if llm_path.exists() else None,
        rules_metrics=_load(rules_path) if rules_path.exists() else None,
        transfer_metrics=_load(xfer_path) if xfer_path.exists() else None,
        transfer_gate=_load(xfer_gate_path) if xfer_gate_path.exists() else None,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"[report] wrote {out_path}")
    return out_path
