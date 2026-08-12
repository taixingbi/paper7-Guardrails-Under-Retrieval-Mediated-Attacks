"""Concurrent batch helpers (sync ThreadPool — I/O-bound LLM)."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
R = TypeVar("R")


def map_concurrent(
    items: Iterable[T],
    fn: Callable[[T], R],
    *,
    max_concurrency: int = 4,
    desc: str | None = None,
) -> list[R]:
    seq = list(items)
    if not seq:
        return []
    workers = max(1, int(max_concurrency))
    if workers == 1 or len(seq) == 1:
        if desc:
            try:
                from tqdm import tqdm

                seq_iter = tqdm(seq, desc=desc)
            except Exception:
                seq_iter = seq
            return [fn(item) for item in seq_iter]
        return [fn(item) for item in seq]

    results: list[R | None] = [None] * len(seq)
    with ThreadPoolExecutor(max_workers=workers) as pool:
        future_to_idx = {pool.submit(fn, item): i for i, item in enumerate(seq)}
        done = as_completed(future_to_idx)
        if desc:
            try:
                from tqdm import tqdm

                done = tqdm(done, total=len(seq), desc=desc)
            except Exception:
                pass
        for fut in done:
            idx = future_to_idx[fut]
            results[idx] = fut.result()
    return results  # type: ignore[return-value]
