from __future__ import annotations

import zlib
from collections import defaultdict
from pathlib import Path
from typing import Any

from gurma.eval.bootstrap import bootstrap_ci, fmt_ci
from gurma.eval.success import INSTRUCTION_SAFETY_ATTACKS, POISONING_ATTACK
from gurma.io import write_json
from gurma.schemas.models import RunRecord


def _stable_offset(label: str, base: int) -> int:
    return base + (zlib.adler32(label.encode("utf-8")) % 1000)


def _rate(vals: list[bool]) -> float | None:
    if not vals:
        return None
    return sum(1 for v in vals if v) / len(vals)


def aggregate_metrics(
    records: list[RunRecord],
    *,
    bootstrap_n: int = 2000,
    bootstrap_seed: int = 0,
) -> dict[str, Any]:
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
                "instruction_safety_asr_ci": bootstrap_ci(
                    safety, n_boot=bootstrap_n, seed=bootstrap_seed
                ),
                "poisoning_success_rate": _rate(psr),
                "poisoning_success_rate_ci": bootstrap_ci(
                    psr, n_boot=bootstrap_n, seed=bootstrap_seed + 1
                ),
                "macro_attack_success": _rate(macro),
                "macro_attack_success_ci": bootstrap_ci(
                    macro, n_boot=bootstrap_n, seed=bootstrap_seed + 2
                ),
                "task_accuracy": _rate(acc),
                "task_accuracy_ci": bootstrap_ci(
                    acc, n_boot=bootstrap_n, seed=bootstrap_seed + 3
                ),
                "over_refusal": _rate(over_ref),
                "over_refusal_ci": bootstrap_ci(
                    over_ref, n_boot=bootstrap_n, seed=bootstrap_seed + 4
                ),
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
            row[f"{g}_success_ci"] = bootstrap_ci(
                vals, n_boot=bootstrap_n, seed=_stable_offset(f"{atype}|{g}", bootstrap_seed + 10)
            )
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
            row[f"{g}_safety_asr_ci"] = bootstrap_ci(
                vals, n_boot=bootstrap_n, seed=_stable_offset(f"{model}|{g}", bootstrap_seed + 20)
            )
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

    # Latency / cost overhead (from RunRecord.metadata when present)
    cost_table: list[dict[str, Any]] = []
    for g in sorted(by_guard.keys()):
        rows = by_guard[g]
        totals = [
            float((r.metadata or {}).get("latency_ms", {}).get("total"))
            for r in rows
            if isinstance((r.metadata or {}).get("latency_ms"), dict)
            and (r.metadata or {}).get("latency_ms", {}).get("total") is not None
        ]
        calls = [
            int((r.metadata or {}).get("n_llm_calls", 0))
            for r in rows
            if (r.metadata or {}).get("n_llm_calls") is not None
        ]
        totals_sorted = sorted(totals)
        p50 = totals_sorted[len(totals_sorted) // 2] if totals_sorted else None
        p95 = (
            totals_sorted[min(len(totals_sorted) - 1, int(0.95 * len(totals_sorted)))]
            if totals_sorted
            else None
        )
        cost_table.append(
            {
                "guardrail": g,
                "n": len(rows),
                "mean_latency_ms": (sum(totals) / len(totals)) if totals else None,
                "p50_latency_ms": p50,
                "p95_latency_ms": p95,
                "mean_llm_calls": (sum(calls) / len(calls)) if calls else None,
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
        "table_cost_latency": cost_table,
        "note": (
            "Instruction/Safety ASR excludes context_poisoning (reported as PSR). "
            "Macro attack success averages all four attack types. "
            "Counts are experimental conditions, not LLM API calls. "
            "Brackets are 95% bootstrap CIs. "
            "Latency/LLM-call stats come from RunRecord.metadata when tracked."
        ),
        "bootstrap_n": bootstrap_n,
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
            f"| {row['guardrail']} | "
            f"{fmt_ci(row['instruction_safety_asr'], row.get('instruction_safety_asr_ci'))} | "
            f"{fmt_ci(row['poisoning_success_rate'], row.get('poisoning_success_rate_ci'))} | "
            f"{fmt_ci(row['macro_attack_success'], row.get('macro_attack_success_ci'))} | "
            f"{fmt_ci(row['task_accuracy'], row.get('task_accuracy_ci'))} | "
            f"{fmt_ci(row['over_refusal'], row.get('over_refusal_ci'))} |"
        )
    lines += [
        "",
        "## Table 3 — Attack breakdown",
        "",
    ]
    guard_order = sorted((metrics.get("table2_main") or []), key=lambda r: r["guardrail"])
    gcols = [r["guardrail"] for r in guard_order] or ["G0", "G1", "G2"]
    lines.append("| Attack | " + " | ".join(gcols) + " |")
    lines.append("|---|" + "|".join(["---:"] * len(gcols)) + "|")
    for row in metrics.get("table3_attack_breakdown") or []:
        cells = [str(row.get("attack"))]
        for g in gcols:
            cells.append(fmt_ci(row.get(f"{g}_success"), row.get(f"{g}_success_ci")))
        lines.append("| " + " | ".join(cells) + " |")
    lines += [
        "",
        "## Table 4 — Cross-model Safety ASR",
        "",
    ]
    lines.append("| Model | " + " | ".join(gcols) + " |")
    lines.append("|---|" + "|".join(["---:"] * len(gcols)) + "|")
    for row in metrics.get("table4_cross_model") or []:
        cells = [str(row.get("model"))]
        for g in gcols:
            cells.append(fmt_ci(row.get(f"{g}_safety_asr"), row.get(f"{g}_safety_asr_ci")))
        lines.append("| " + " | ".join(cells) + " |")
    if metrics.get("table_cost_latency"):
        lines += [
            "",
            "## Cost / latency",
            "",
            "| Guardrail | n | mean ms | p50 ms | p95 ms | mean LLM calls |",
            "|---|---:|---:|---:|---:|---:|",
        ]
        for row in metrics["table_cost_latency"]:
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
    return "\n".join(lines)


def write_metrics_report(
    path: Path,
    records: list[RunRecord],
    *,
    bootstrap_n: int = 2000,
    bootstrap_seed: int = 0,
) -> dict[str, Any]:
    metrics = aggregate_metrics(
        records, bootstrap_n=bootstrap_n, bootstrap_seed=bootstrap_seed
    )
    write_json(path / "metrics.json", metrics)
    (path / "metrics.md").write_text(metrics_to_markdown(metrics))
    return metrics
