"""Bootstrap 95% CIs for binary rates."""

from __future__ import annotations

import random
from typing import Any


def bootstrap_ci(
    vals: list[bool],
    *,
    n_boot: int = 2000,
    alpha: float = 0.05,
    seed: int = 0,
) -> dict[str, Any]:
    n = len(vals)
    if n == 0:
        return {"low": None, "high": None, "n": 0, "n_boot": n_boot}
    rng = random.Random(seed)
    arr = [1.0 if v else 0.0 for v in vals]
    stats: list[float] = []
    for _ in range(n_boot):
        total = 0.0
        for _i in range(n):
            total += arr[rng.randrange(n)]
        stats.append(total / n)
    stats.sort()
    lo_idx = min(n_boot - 1, max(0, int((alpha / 2) * n_boot)))
    hi_idx = min(n_boot - 1, max(0, int((1 - alpha / 2) * n_boot)))
    return {
        "low": stats[lo_idx],
        "high": stats[hi_idx],
        "n": n,
        "n_boot": n_boot,
    }


def fmt_ci(point: float | None, ci: dict[str, Any] | None, digits: int = 3) -> str:
    if point is None:
        return "—"
    base = f"{point:.{digits}f}"
    if not ci or ci.get("low") is None or ci.get("high") is None:
        return base
    return f"{base} [{ci['low']:.{digits}f}, {ci['high']:.{digits}f}]"
