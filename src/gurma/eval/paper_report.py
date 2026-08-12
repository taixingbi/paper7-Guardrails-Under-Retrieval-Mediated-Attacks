"""Generate a paper-facing results report from saved metrics JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]


def _load(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(path)
    return json.loads(path.read_text())


def _fmt(x: Any, digits: int = 3) -> str:
    if x is None:
        return "—"
    return f"{float(x):.{digits}f}"


def _row(guard: dict[str, Any]) -> str:
    return (
        f"| {guard['guardrail']} "
        f"| {_fmt(guard.get('instruction_safety_asr'))} "
        f"| {_fmt(guard.get('poisoning_success_rate'))} "
        f"| {_fmt(guard.get('macro_attack_success'))} "
        f"| {_fmt(guard.get('task_accuracy'))} "
        f"| {_fmt(guard.get('over_refusal'))} |"
    )


def render_paper_report(
    *,
    main_metrics: dict[str, Any],
    main_gate: dict[str, Any],
    ablation: dict[str, Any],
    llm_metrics: dict[str, Any] | None = None,
    rules_metrics: dict[str, Any] | None = None,
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
        "Generated from frozen main + input ablations. "
        "Regenerate with `gurma paper-report`.",
        "",
        "## Setup",
        "",
        "- Seeds: 100 HotpotQA (both-model clean freeze)",
        "- Attacks: 4 × 100 = 400 validated cases (`accepted = semantic ∧ payload`)",
        "- Guardrails: G0 none / G1 input / G2 input+output",
        "- Models: `nova-pro`, `llama`; guard/judge: `gpt-oss`",
        "- Defense freeze: hybrid input (`rules` first) + `v3` prompts ([FREEZE.md](../FREEZE.md))",
        "- Main conditions: 3000 (2400 attack + 600 clean); API calls ≫ 3000",
        "",
        "## Findings",
        "",
        "1. **G0 is highly vulnerable** to retrieval-mediated instruction attacks "
        f"(Safety ASR {_fmt(t2[0].get('instruction_safety_asr') if t2 else None)}; "
        "A1 = 0.905). Llama is much weaker than Nova Pro on G0 (0.977 vs 0.393).",
        "2. **Hybrid G1 eliminates instruction/safety attacks** (Safety ASR 0.000) "
        "and raises attacked-task accuracy 0.279 → 0.820 with ~0 over-refusal.",
        "3. **G2 adds almost nothing on hybrid** (rescue 10/517 G0 successes after G1). "
        "G2 rewrite is rare (11), so accuracy is not rewrite-inflated.",
        "4. **Ablation:** rules-only also reaches Safety ASR 0.000; LLM-only remains "
        "0.457. Hybrid mainly improves **PSR** vs rules (0.300 vs 0.415).",
        "5. **Limitation:** context poisoning remains (PSR ≈ 0.30 under hybrid G1/G2).",
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
        "Macro = mean over all four. Acc = task accuracy on attacked cases.",
        "",
        "## Table 3 — Attack breakdown",
        "",
        "| Attack | G0 | G1 | G2 |",
        "|---|---:|---:|---:|",
    ]
    for row in t3:
        lines.append(
            f"| {row.get('attack')} | {_fmt(row.get('G0_success'))} "
            f"| {_fmt(row.get('G1_success'))} | {_fmt(row.get('G2_success'))} |"
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
            f"| {row.get('model')} | {_fmt(row.get('G0_safety_asr'))} "
            f"| {_fmt(row.get('G1_safety_asr'))} | {_fmt(row.get('G2_safety_asr'))} |"
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
            f"| {row.get('input_mode')} | {_fmt(row.get('safety_asr'))} "
            f"| {_fmt(row.get('psr'))} | {_fmt(row.get('macro'))} "
            f"| {_fmt(row.get('task_accuracy'))} | {_fmt(row.get('over_refusal'))} |"
        )
    lines += [
        "",
        "G0 rows for rules/llm ablations are borrowed from main. "
        "Hybrid = rules first, then LLM residual.",
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
                f"| {row['guardrail']} | {_fmt(row.get('instruction_safety_asr'))} "
                f"| {_fmt(row.get('poisoning_success_rate'))} "
                f"| {_fmt(row.get('task_accuracy'))} "
                f"| {_fmt(row.get('over_refusal'))} |"
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
                f"| {row['guardrail']} | {_fmt(row.get('instruction_safety_asr'))} "
                f"| {_fmt(row.get('poisoning_success_rate'))} "
                f"| {_fmt(row.get('task_accuracy'))} "
                f"| {_fmt(row.get('over_refusal'))} |"
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
        "## Caveats",
        "",
        "- Counts are **experimental conditions**, not LLM API calls.",
        "- A2 success is an integrity metric (PSR), not Safety ASR.",
        "- Attack acceptance never uses G0 effectiveness (no selection bias).",
        "- Hybrid rules match known operator templates; transfer to novel phrasing is untested.",
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
    md = render_paper_report(
        main_metrics=main_metrics,
        main_gate=main_gate,
        ablation=ablation,
        llm_metrics=_load(llm_path) if llm_path.exists() else None,
        rules_metrics=_load(rules_path) if rules_path.exists() else None,
    )
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md)
    print(f"[report] wrote {out_path}")
    return out_path
