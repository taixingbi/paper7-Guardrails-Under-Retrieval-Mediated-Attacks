"""Compare hybrid / rules-only / LLM-only ablation metrics."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


DEFAULT_RUNS = {
    "hybrid": Path("data/runs/main/6_metrics/metrics.json"),
    "rules": Path("data/runs/main_ablation_rules/6_metrics/metrics.json"),
    "llm": Path("data/runs/main_ablation_llm/6_metrics/metrics.json"),
}


def _g1_row(metrics: dict[str, Any]) -> dict[str, Any] | None:
    for row in metrics.get("table2_main") or []:
        if row.get("guardrail") == "G1":
            return row
    return None


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
        g1 = _g1_row(metrics) or {}
        rows.append(
            {
                "input_mode": name,
                "safety_asr": g1.get("instruction_safety_asr"),
                "psr": g1.get("poisoning_success_rate"),
                "macro": g1.get("macro_attack_success"),
                "task_accuracy": g1.get("task_accuracy"),
                "over_refusal": g1.get("over_refusal"),
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

    def fmt(x: Any) -> str:
        return "—" if x is None else f"{float(x):.3f}"

    for row in rows:
        lines.append(
            f"| {row['input_mode']} | {fmt(row['safety_asr'])} | {fmt(row['psr'])} | "
            f"{fmt(row['macro'])} | {fmt(row['task_accuracy'])} | {fmt(row['over_refusal'])} |"
        )
    if missing:
        lines += ["", "## Missing", ""] + [f"- {m}" for m in missing]
    lines.append("")
    (out_dir / "ablation_compare.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return report
