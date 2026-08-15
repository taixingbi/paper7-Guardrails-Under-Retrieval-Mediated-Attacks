"""Compare hybrid / rules-only / LLM-only ablation metrics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gurma.eval.bootstrap import fmt_ci
from gurma.eval.metrics_io import g1_row


DEFAULT_RUNS = {
    "hybrid": Path("data/runs/main/6_metrics/metrics.json"),
    "rules": Path("data/runs/main_ablation_rules/6_metrics/metrics.json"),
    "llm": Path("data/runs/main_ablation_llm/6_metrics/metrics.json"),
}


def build_ablation_report(
    runs: dict[str, Path] | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    runs = runs or DEFAULT_RUNS
    out_dir = out_dir or Path("data/runs/ablation_compare")
    out_dir.mkdir(parents=True, exist_ok=True)

    loaded: dict[str, dict[str, Any]] = {}
    missing: list[str] = []
    for name, path in runs.items():
        if not path.exists():
            missing.append(f"{name}:{path}")
            continue
        loaded[name] = json.loads(path.read_text())

    rows = []
    for name, metrics in loaded.items():
        g1 = g1_row(metrics)
        rows.append(
            {
                "input_mode": name,
                "safety_asr": g1.get("instruction_safety_asr"),
                "safety_asr_ci": g1.get("instruction_safety_asr_ci"),
                "psr": g1.get("poisoning_success_rate"),
                "psr_ci": g1.get("poisoning_success_rate_ci"),
                "macro": g1.get("macro_attack_success"),
                "macro_ci": g1.get("macro_attack_success_ci"),
                "task_accuracy": g1.get("task_accuracy"),
                "task_accuracy_ci": g1.get("task_accuracy_ci"),
                "over_refusal": g1.get("over_refusal"),
                "over_refusal_ci": g1.get("over_refusal_ci"),
            }
        )

    report = {
        "missing": missing,
        "g1_comparison": rows,
        "note": (
            "G0 borrowed from main for rules/llm ablations. "
            "Compare G1 to isolate input-component contribution."
        ),
    }
    (out_dir / "ablation_compare.json").write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Input Guardrail Ablation (G1)",
        "",
        report["note"],
        "",
        "| Input mode | Safety ASR | PSR | Macro | Acc | Over-refusal |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for row in rows:
        lines.append(
            f"| {row['input_mode']} | "
            f"{fmt_ci(row['safety_asr'], row.get('safety_asr_ci'))} | "
            f"{fmt_ci(row['psr'], row.get('psr_ci'))} | "
            f"{fmt_ci(row['macro'], row.get('macro_ci'))} | "
            f"{fmt_ci(row['task_accuracy'], row.get('task_accuracy_ci'))} | "
            f"{fmt_ci(row['over_refusal'], row.get('over_refusal_ci'))} |"
        )
    if missing:
        lines += ["", "## Missing", ""] + [f"- {m}" for m in missing]
    lines.append("")
    (out_dir / "ablation_compare.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return report
