"""Shared G1 metric-row helpers for compare reports."""

from __future__ import annotations

from typing import Any


def g1_row(metrics: dict[str, Any]) -> dict[str, Any]:
    for row in metrics.get("table2_main") or []:
        if row.get("guardrail") == "G1":
            return row
    return {}


def cost_g1(metrics: dict[str, Any]) -> dict[str, Any]:
    for row in metrics.get("table_cost_latency") or []:
        if row.get("guardrail") == "G1":
            return row
    return {}


def fmt_ms(x: Any) -> str:
    return "—" if x is None else f"{float(x):.1f}"


def fmt_calls(x: Any) -> str:
    return "—" if x is None else f"{float(x):.2f}"
