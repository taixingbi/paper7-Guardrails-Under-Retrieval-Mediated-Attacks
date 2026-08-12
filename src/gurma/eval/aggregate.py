from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Any

from gurma.eval.success import INSTRUCTION_SAFETY_ATTACKS, POISONING_ATTACK
from gurma.io import write_json
from gurma.schemas.models import RunRecord


def _rate(vals: list[bool]) -> float | None:
    if not vals:
        return None
    return sum(1 for v in vals if v) / len(vals)


def aggregate_metrics(records: list[RunRecord]) -> dict[str, Any]:
    clean = [r for r in records if not r.attack_type or r.attack_type == "clean"]
    attacked = [r for r in records if r.attack_type and r.attack_type != "clean"]

    by_guard: dict[str, list[RunRecord]] = defaultdict(list)
    for r in records:
        by_guard[r.guardrail].append(r)

    table2: list[dict[str, Any]] = []
    for g in sorted(by_guard.keys()):
        rows = by_guard[g]
        clean_g = [r for r in rows if not r.attack_type or r.attack_type == "clean"]
        atk_g = [r for r in rows if r.attack_type and r.attack_type != "clean"]
        safety = [
            bool(r.attack_success)
            for r in atk_g
            if r.attack_type in INSTRUCTION_SAFETY_ATTACKS and r.attack_success is not None
        ]
        psr = [
            bool(r.attack_success)
            for r in atk_g
            if r.attack_type == POISONING_ATTACK and r.attack_success is not None
        ]
        macro = [bool(r.attack_success) for r in atk_g if r.attack_success is not None]
        acc = [bool(r.answer_correct) for r in atk_g if r.answer_correct is not None]
        over_ref = [bool(r.refused) for r in clean_g]
        safety_viol = [bool(r.safety_violation) for r in atk_g]
        table2.append(
            {
                "guardrail": g,
                "instruction_safety_asr": _rate(safety),
                "poisoning_success_rate": _rate(psr),
                "macro_attack_success": _rate(macro),
                "task_accuracy": _rate(acc),
                "over_refusal": _rate(over_ref),
                "safety_violation_rate": _rate(safety_viol),
                "n_attack": len(atk_g),
                "n_clean": len(clean_g),
            }
        )

    # Table 3: attack × guardrail success
    table3: list[dict[str, Any]] = []
    attacks = sorted({r.attack_type for r in attacked if r.attack_type})
    for atype in attacks:
        row: dict[str, Any] = {"attack": atype}
        for g in sorted(by_guard.keys()):
            vals = [
                bool(r.attack_success)
                for r in by_guard[g]
                if r.attack_type == atype and r.attack_success is not None
            ]
            row[f"{g}_success"] = _rate(vals)
        table3.append(row)

    # Table 4: model × guardrail safety ASR
    table4: list[dict[str, Any]] = []
    models = sorted({r.model for r in records})
    for model in models:
        row: dict[str, Any] = {"model": model}
        for g in sorted(by_guard.keys()):
            vals = [
                bool(r.attack_success)
                for r in records
                if r.model == model
                and r.guardrail == g
                and r.attack_type in INSTRUCTION_SAFETY_ATTACKS
                and r.attack_success is not None
            ]
            row[f"{g}_safety_asr"] = _rate(vals)
        table4.append(row)

    table1 = {
        atype: sum(1 for r in attacked if r.attack_type == atype and r.guardrail == "G0")
        // max(1, len(models))
        for atype in attacks
    }

    # Points for Safety-ASR vs benign accuracy scatter (paper figure)
    scatter = []
    for row in table2:
        scatter.append(
            {
                "guardrail": row["guardrail"],
                "safety_asr": row["instruction_safety_asr"],
                "benign_accuracy": (
                    _rate(
                        [
                            bool(r.answer_correct)
                            for r in by_guard[row["guardrail"]]
                            if (not r.attack_type or r.attack_type == "clean")
                            and r.answer_correct is not None
                        ]
                    )
                ),
                "task_accuracy_on_attacks": row["task_accuracy"],
                "over_refusal": row["over_refusal"],
            }
        )

    return {
        "n_records": len(records),
        "n_clean_conditions": len(clean),
        "n_attack_conditions": len(attacked),
        "table1_dataset": table1,
        "table2_main": table2,
        "table3_attack_breakdown": table3,
        "table4_cross_model": table4,
        "scatter_safety_vs_benign_acc": scatter,
        "note": (
            "Instruction/Safety ASR excludes context_poisoning (reported as PSR). "
            "Macro attack success averages all four attack types. "
            "Counts are experimental conditions, not LLM API calls."
        ),
    }


def metrics_to_markdown(metrics: dict[str, Any]) -> str:
    lines = [
        "# GURMA Metrics",
        "",
        metrics.get("note", ""),
        "",
        f"Records: {metrics.get('n_records')} "
        f"(clean={metrics.get('n_clean_conditions')}, attack={metrics.get('n_attack_conditions')})",
        "",
        "## Table 1 — Dataset (G0 cases / model)",
        "",
    ]
    for k, v in (metrics.get("table1_dataset") or {}).items():
        lines.append(f"- {k}: {v}")
    lines += ["", "## Table 2 — Main", "", "| Guardrail | Safety ASR | PSR | Macro | Acc | Over-refusal |", "|---|---:|---:|---:|---:|---:|"]
    for row in metrics.get("table2_main") or []:
        def fmt(x: float | None) -> str:
            return "—" if x is None else f"{x:.3f}"

        lines.append(
            f"| {row['guardrail']} | {fmt(row['instruction_safety_asr'])} | "
            f"{fmt(row['poisoning_success_rate'])} | {fmt(row['macro_attack_success'])} | "
            f"{fmt(row['task_accuracy'])} | {fmt(row['over_refusal'])} |"
        )
    lines += ["", "## Table 3 — Attack breakdown", ""]
    for row in metrics.get("table3_attack_breakdown") or []:
        lines.append(f"- {row}")
    lines += ["", "## Table 4 — Cross-model Safety ASR", ""]
    for row in metrics.get("table4_cross_model") or []:
        lines.append(f"- {row}")
    lines.append("")
    return "\n".join(lines)


def write_metrics_report(path: Path, records: list[RunRecord]) -> dict[str, Any]:
    metrics = aggregate_metrics(records)
    write_json(path / "metrics.json", metrics)
    (path / "metrics.md").write_text(metrics_to_markdown(metrics))
    return metrics
