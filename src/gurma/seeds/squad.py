"""SQuAD single-hop seeds for cross-dataset transfer (defense frozen on HotpotQA)."""

from __future__ import annotations

import random
from pathlib import Path

from gurma.config import AppConfig
from gurma.io import load_models, write_jsonl
from gurma.schemas.models import CleanSeed


def _candidate_ok(seed: CleanSeed, cfg: AppConfig) -> bool:
    if not seed.question.strip() or not seed.gold_answer.strip():
        return False
    if not seed.supporting_context:
        return False
    ctx = seed.clean_context_text()
    if len(ctx) < cfg.min_context_chars or len(ctx) > cfg.max_context_chars:
        return False
    return True


def load_squad_candidates(cfg: AppConfig, *, rng: random.Random | None = None) -> list[CleanSeed]:
    rng = rng or random.Random(42)
    if cfg.use_fixture_seeds:
        path = Path(cfg.fixture_seeds_path)
        return load_models(path, CleanSeed)[: cfg.candidate_limit]

    from datasets import load_dataset

    ds = load_dataset(cfg.squad_dataset, split=cfg.squad_split)
    indices = list(range(len(ds)))
    rng.shuffle(indices)

    seeds: list[CleanSeed] = []
    for idx in indices:
        if len(seeds) >= cfg.candidate_limit:
            break
        ex = ds[int(idx)]
        answers = ex.get("answers") or {}
        texts = list(answers.get("text") or [])
        if not texts:
            continue
        answer = str(texts[0]).strip()
        question = str(ex.get("question") or "").strip()
        context = str(ex.get("context") or "").strip()
        title = str(ex.get("title") or "Passage").strip()
        if not answer or not question or not context:
            continue
        # Skip yes/no-ish
        if answer.lower() in {"yes", "no"}:
            continue
        supporting = [f"Title: {title}\n{context}"]
        seed = CleanSeed(
            seed_id=f"sq_{len(seeds) + 1:06d}",
            question=question,
            gold_answer=answer,
            supporting_context=supporting,
            distractor_context=[],
            metadata={
                "dataset": "squad",
                "squad_id": ex.get("id"),
                "source_index": int(idx),
            },
        )
        if not _candidate_ok(seed, cfg):
            continue
        seeds.append(seed)
    return seeds
