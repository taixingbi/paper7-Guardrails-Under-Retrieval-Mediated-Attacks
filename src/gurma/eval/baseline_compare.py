"""Compare GURMA hybrid vs external baselines vs ablations (G1)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gurma.eval.bootstrap import fmt_ci

DEFAULT_RUNS = {
    "hybrid": Path("data/runs/main/6_metrics/metrics.json"),
    "rules": Path("data/runs/main_ablation_rules/6_metrics/metrics.json"),
    "llm": Path("data/runs/main_ablation_llm/6_metrics/metrics.json"),
    "pi_detector": Path("data/runs/main_baseline_pi/6_metrics/metrics.json"),
    "moderation": Path("data/runs/main_baseline_mod/6_metrics/metrics.json"),
}


def _g1_row(metrics: dict[str, Any]) -> dict[str, Any] | None:
    for row in metrics.get("table2_main") or []:
        if row.get("guardrail") == "G1":
            return row
    return None


def _cost_g1(metrics: dict[str, Any]) -> dict[str, Any]:
    for row in metrics.get("table_cost_latency") or []:
        if row.get("guardrail") == "G1":
            return row
    return {}


def build_baseline_compare(
    runs: dict[str, Path] | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    runs = runs or DEFAULT_RUNS
    out_dir = out_dir or Path("data/runs/baseline_compare")
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
        cost = _cost_g1(metrics)
        rows.append(
            {
                "defense": name,
                "safety_asr": g1.get("instruction_safety_asr"),
                "safety_asr_ci": g1.get("instruction_safety_asr_ci"),
                "psr": g1.get("poisoning_success_rate"),
                "psr_ci": g1.get("poisoning_success_rate_ci"),
                "task_accuracy": g1.get("task_accuracy"),
                "task_accuracy_ci": g1.get("task_accuracy_ci"),
                "mean_latency_ms": cost.get("mean_latency_ms"),
                "mean_llm_calls": cost.get("mean_llm_calls"),
                "n_attack": g1.get("n_attack"),
            }
        )

    report = {
        "missing": missing,
        "g1_comparison": rows,
        "note": (
            "G1-only comparison across GURMA input modes and external baselines. "
            "pi_detector / moderation are not GURMA template rules. "
            "Baseline runs may use seed_limit=50; check n_attack."
        ),
    }
    (out_dir / "baseline_compare.json").write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Defense Comparison (G1)",
        "",
        report["note"],
        "",
        "| Defense | Safety ASR | PSR | Acc | mean ms | LLM calls | n |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lat = row.get("mean_latency_ms")
        calls = row.get("mean_llm_calls")
        lines.append(
            f"| {row['defense']} | "
            f"{fmt_ci(row['safety_asr'], row.get('safety_asr_ci'))} | "
            f"{fmt_ci(row['psr'], row.get('psr_ci'))} | "
            f"{fmt_ci(row['task_accuracy'], row.get('task_accuracy_ci'))} | "
            f"{('—' if lat is None else f'{lat:.1f}')} | "
            f"{('—' if calls is None else f'{calls:.2f}')} | "
            f"{row.get('n_attack', '—')} |"
        )
    if missing:
        lines += ["", "## Missing", ""] + [f"- {m}" for m in missing]
    lines.append("")
    (out_dir / "baseline_compare.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return report
