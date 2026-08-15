"""Re-aggregate existing run_records on a shared 50-seed freeze subset (no LLM)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from gurma.eval.aggregate import write_metrics_report
from gurma.io import load_models
from gurma.schemas.models import RunRecord, ValidatedSeed

CANONICAL_50 = Path("data/runs/main_guard_ministral_3b/2_validated_seeds/validated_seeds.jsonl")
MAIN_SEEDS = Path("data/runs/main/2_validated_seeds/validated_seeds.jsonl")


def matched_seed_ids(*, n: int = 50) -> list[str]:
    """First-n freeze seeds used by seed_limit=50 reuse runs."""
    for path in (CANONICAL_50, MAIN_SEEDS):
        if not path.exists():
            continue
        ids = [s.seed_id for s in load_models(path, ValidatedSeed)]
        return ids[:n]
    raise FileNotFoundError("Need validated_seeds.jsonl to resolve matched 50-seed subset")


def write_seed_subset_metrics(
    records_path: Path,
    out_dir: Path,
    *,
    bootstrap_n: int = 2000,
    bootstrap_seed: int = 0,
    label: str = "subset",
) -> dict[str, Any]:
    if not records_path.exists():
        print(f"[matched] skip {label} (missing {records_path})")
        return {}
    keep = set(matched_seed_ids())
    records = [r for r in load_models(records_path, RunRecord) if r.seed_id in keep]
    metrics_dir = out_dir / "6_metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    metrics = write_metrics_report(
        metrics_dir,
        records,
        bootstrap_n=bootstrap_n,
        bootstrap_seed=bootstrap_seed,
    )
    (out_dir / "matched_seed_ids.json").write_text(
        json.dumps({"n_seeds": len(keep), "seed_ids": sorted(keep), "source": str(records_path)}, indent=2)
        + "\n"
    )
    print(f"[matched] {label} seeds={len(keep)} records={len(records)} → {metrics_dir}")
    return metrics
