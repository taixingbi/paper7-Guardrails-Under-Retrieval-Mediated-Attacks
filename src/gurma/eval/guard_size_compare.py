"""Compare guardrail LLM sizes (G1) under frozen hybrid v3."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gurma.eval.bootstrap import fmt_ci

# Ministral size ladder + frozen main gpt-oss (120B) reference.
# Aliases from https://github.com/taixingbi/mvp-bedrock/blob/main/example.md
DEFAULT_RUNS = {
    "ministral-3b": Path("data/runs/main_guard_ministral_3b/6_metrics/metrics.json"),
    "ministral-8b": Path("data/runs/main_guard_ministral_8b/6_metrics/metrics.json"),
    "ministral-14b": Path("data/runs/main_guard_ministral_14b/6_metrics/metrics.json"),
    "gpt-oss (120B, main)": Path("data/runs/main/6_metrics/metrics.json"),
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


def build_guard_size_compare(
    runs: dict[str, Path] | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    runs = runs or DEFAULT_RUNS
    out_dir = out_dir or Path("data/runs/guard_size_compare")
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
                "guard_model": name,
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
            "Frozen hybrid v3; only the guardrail LLM changes. "
            "Ministral 3B/8B/14B are a size ladder; gpt-oss is the main 120B reference "
            "(full main n may differ from seed_limit=50 Ministral runs). "
            "Rules fire first — expect limited Safety ASR movement in-distribution."
        ),
    }
    (out_dir / "guard_size_compare.json").write_text(json.dumps(report, indent=2) + "\n")

    lines = [
        "# Guardrail model-size ablation (G1, hybrid v3)",
        "",
        report["note"],
        "",
        "| Guard LLM | Safety ASR | PSR | Acc | mean ms | LLM calls | n |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lat = row.get("mean_latency_ms")
        calls = row.get("mean_llm_calls")
        lines.append(
            f"| {row['guard_model']} | "
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
    (out_dir / "guard_size_compare.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return report
