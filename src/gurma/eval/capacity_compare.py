"""Experiment 6 — Guard model capacity: size × (LLM-only | hybrid)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gurma.eval.bootstrap import fmt_ci

# S/M/L from mvp-bedrock aliases; target fixed to nova-pro, G1 only.
CELLS: list[tuple[str, str, str, Path]] = [
    ("llm", "S", "ministral-3b (~3B)", Path("data/runs/main_e6_llm_s/6_metrics/metrics.json")),
    ("llm", "M", "ministral-14b (~14B)", Path("data/runs/main_e6_llm_m/6_metrics/metrics.json")),
    ("llm", "L", "llama (~70B)", Path("data/runs/main_e6_llm_l/6_metrics/metrics.json")),
    ("hybrid", "S", "ministral-3b (~3B)", Path("data/runs/main_e6_hybrid_s/6_metrics/metrics.json")),
    ("hybrid", "M", "ministral-14b (~14B)", Path("data/runs/main_e6_hybrid_m/6_metrics/metrics.json")),
    ("hybrid", "L", "llama (~70B)", Path("data/runs/main_e6_hybrid_l/6_metrics/metrics.json")),
]


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


def build_capacity_compare(out_dir: Path | None = None) -> dict[str, Any]:
    out_dir = out_dir or Path("data/runs/e6_capacity_compare")
    out_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for mode, size, label, path in CELLS:
        if not path.exists():
            missing.append(f"{mode}/{size}:{path}")
            continue
        metrics = json.loads(path.read_text())
        g1 = _g1_row(metrics) or {}
        cost = _cost_g1(metrics)
        rows.append(
            {
                "mode": mode,
                "size": size,
                "guard_model": label,
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
        "cells": rows,
        "note": (
            "Experiment 6 — Guard model capacity. "
            "Fixed: target=nova-pro, placement=G1/context, v3 prompts, same attacks "
            "(50 seeds). Vary: guard LLM size (S/M/L) and input mode (LLM-only vs hybrid). "
            "RQ1: does scaling improve robustness? "
            "RQ2: does a larger guard eliminate the need for deterministic rules?"
        ),
        "rqs": [
            "RQ1: Does scaling the guard model improve robustness?",
            "RQ2: Does a larger guard model eliminate the need for deterministic rules?",
        ],
    }
    (out_dir / "e6_capacity_compare.json").write_text(json.dumps(report, indent=2) + "\n")

    def _lat(x: Any) -> str:
        return "—" if x is None else f"{float(x):.1f}"

    def _calls(x: Any) -> str:
        return "—" if x is None else f"{float(x):.2f}"

    lines = [
        "# Experiment 6 — Guard model capacity",
        "",
        report["note"],
        "",
        "## Full grid (G1)",
        "",
        "| Mode | Size | Guard LLM | Safety ASR | PSR | Acc | mean ms | LLM calls | n |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['mode']} | {row['size']} | {row['guard_model']} | "
            f"{fmt_ci(row['safety_asr'], row.get('safety_asr_ci'))} | "
            f"{fmt_ci(row['psr'], row.get('psr_ci'))} | "
            f"{fmt_ci(row['task_accuracy'], row.get('task_accuracy_ci'))} | "
            f"{_lat(row.get('mean_latency_ms'))} | "
            f"{_calls(row.get('mean_llm_calls'))} | "
            f"{row.get('n_attack', '—')} |"
        )

    # Compact Safety ASR tables for RQ1/RQ2
    by_key = {(r["mode"], r["size"]): r for r in rows}
    lines += [
        "",
        "## Safety ASR by mode × size",
        "",
        "| Mode | S (3B) | M (14B) | L (70B) |",
        "|---|---:|---:|---:|",
    ]
    for mode in ("llm", "hybrid"):
        cells = []
        for size in ("S", "M", "L"):
            r = by_key.get((mode, size))
            cells.append(
                "—"
                if r is None
                else fmt_ci(r["safety_asr"], r.get("safety_asr_ci"))
            )
        lines.append(f"| {mode} | " + " | ".join(cells) + " |")

    lines += [
        "",
        "## PSR by mode × size",
        "",
        "| Mode | S (3B) | M (14B) | L (70B) |",
        "|---|---:|---:|---:|",
    ]
    for mode in ("llm", "hybrid"):
        cells = []
        for size in ("S", "M", "L"):
            r = by_key.get((mode, size))
            cells.append(
                "—" if r is None else fmt_ci(r["psr"], r.get("psr_ci"))
            )
        lines.append(f"| {mode} | " + " | ".join(cells) + " |")

    if missing:
        lines += ["", "## Missing", ""] + [f"- {m}" for m in missing]
    lines.append("")
    (out_dir / "e6_capacity_compare.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return report


XFER_CELLS: list[tuple[str, str, str, Path]] = [
    ("llm", "S", "ministral-3b (~3B)", Path("data/runs/main_xfer_llm_s/6_metrics/metrics.json")),
    ("llm", "M", "ministral-14b (~14B)", Path("data/runs/main_xfer_llm_m/6_metrics/metrics.json")),
    ("llm", "L", "llama (~70B)", Path("data/runs/main_xfer_llm_l/6_metrics/metrics.json")),
    ("hybrid", "S", "ministral-3b (~3B)", Path("data/runs/main_xfer_hybrid_s/6_metrics/metrics.json")),
    ("hybrid", "M", "ministral-14b (~14B)", Path("data/runs/main_xfer_hybrid_m/6_metrics/metrics.json")),
    ("hybrid", "L", "llama (~70B)", Path("data/runs/main_xfer_hybrid_l/6_metrics/metrics.json")),
    (
        "hybrid",
        "120B",
        "gpt-oss (~120B, Exp 4)",
        Path("data/runs/main_transfer/6_metrics/metrics.json"),
    ),
]


def build_xfer_size_compare(out_dir: Path | None = None) -> dict[str, Any]:
    """Guard size × mode on frozen held-out attacks (rules mostly miss)."""
    out_dir = out_dir or Path("data/runs/xfer_size_compare")
    out_dir.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for mode, size, label, path in XFER_CELLS:
        if not path.exists():
            missing.append(f"{mode}/{size}:{path}")
            continue
        metrics = json.loads(path.read_text())
        g1 = _g1_row(metrics) or {}
        cost = _cost_g1(metrics)
        rows.append(
            {
                "mode": mode,
                "size": size,
                "guard_model": label,
                "safety_asr": g1.get("instruction_safety_asr"),
                "safety_asr_ci": g1.get("instruction_safety_asr_ci"),
                "task_accuracy": g1.get("task_accuracy"),
                "task_accuracy_ci": g1.get("task_accuracy_ci"),
                "mean_latency_ms": cost.get("mean_latency_ms"),
                "mean_llm_calls": cost.get("mean_llm_calls"),
                "n_attack": g1.get("n_attack"),
            }
        )
    report = {
        "missing": missing,
        "cells": rows,
        "note": (
            "Guard-size × unseen (held-out) attacks. Same 50 seeds and A1/A3/A4 "
            "templates as Experiment 4. G1 only. Rules mostly miss (~83% allow), "
            "so residual / LLM-only guard size can actually move Safety ASR. "
            "gpt-oss hybrid is the existing Exp-4 G1 row (n=300), not re-inferred."
        ),
    }
    (out_dir / "xfer_size_compare.json").write_text(json.dumps(report, indent=2) + "\n")

    def _lat(x: Any) -> str:
        return "—" if x is None else f"{float(x):.1f}"

    def _calls(x: Any) -> str:
        return "—" if x is None else f"{float(x):.2f}"

    lines = [
        "# Guard-size × unseen attacks (G1)",
        "",
        report["note"],
        "",
        "| Mode | Size | Guard LLM | Safety ASR | Acc | mean ms | LLM calls | n |",
        "|---|---|---|---:|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['mode']} | {row['size']} | {row['guard_model']} | "
            f"{fmt_ci(row['safety_asr'], row.get('safety_asr_ci'))} | "
            f"{fmt_ci(row['task_accuracy'], row.get('task_accuracy_ci'))} | "
            f"{_lat(row.get('mean_latency_ms'))} | "
            f"{_calls(row.get('mean_llm_calls'))} | "
            f"{row.get('n_attack', '—')} |"
        )
    by_key = {(r["mode"], r["size"]): r for r in rows}
    lines += [
        "",
        "## Safety ASR by mode × size",
        "",
        "| Mode | S (3B) | M (14B) | L (70B) | gpt-oss (120B) |",
        "|---|---:|---:|---:|---:|",
    ]
    for mode in ("llm", "hybrid"):
        cells = []
        for size in ("S", "M", "L", "120B"):
            r = by_key.get((mode, size))
            cells.append(
                "—" if r is None else fmt_ci(r["safety_asr"], r.get("safety_asr_ci"))
            )
        lines.append(f"| {mode} | " + " | ".join(cells) + " |")
    if missing:
        lines += ["", "## Missing", ""] + [f"- {m}" for m in missing]
    lines.append("")
    (out_dir / "xfer_size_compare.md").write_text("\n".join(lines))
    print("\n".join(lines))
    return report
