from __future__ import annotations

import random
from pathlib import Path

from gurma.config import AppConfig
from gurma.io import load_models, write_jsonl
from gurma.schemas.models import CleanSeed


def _is_yes_no(answer: str) -> bool:
    return normalize_simple(answer) in {"yes", "no"}


def normalize_simple(text: str) -> str:
    return " ".join((text or "").strip().lower().split())


def _paragraphs_from_context(context: dict) -> tuple[list[str], list[str]]:
    """HotpotQA distractor context: {title: [sentences...]} plus supporting_facts."""
    titles = context.get("title") or []
    sentences = context.get("sentences") or []
    supporting: list[str] = []
    distractors: list[str] = []
    # Prefer caller-provided supporting title set via metadata later; here split heuristically.
    for title, sents in zip(titles, sentences):
        block = f"{title}\n" + " ".join(sents) if isinstance(sents, list) else f"{title}\n{sents}"
        distractors.append(block.strip())
    return supporting, distractors


def _build_contexts(example: dict) -> tuple[list[str], list[str]]:
    ctx = example.get("context") or {}
    titles = list(ctx.get("title") or [])
    sentences = list(ctx.get("sentences") or [])
    sf = example.get("supporting_facts") or {}
    sf_titles = set(sf.get("title") or [])

    supporting: list[str] = []
    distractors: list[str] = []
    for title, sents in zip(titles, sentences):
        if not isinstance(sents, list):
            sents = [str(sents)]
        block = f"Title: {title}\n" + " ".join(str(s) for s in sents)
        block = block.strip()
        if not block:
            continue
        if title in sf_titles:
            supporting.append(block)
        else:
            distractors.append(block)
    # If supporting_facts empty, treat first two as supporting
    if not supporting and distractors:
        supporting = distractors[:2]
        distractors = distractors[2:]
    return supporting, distractors


def _candidate_ok(seed: CleanSeed, cfg: AppConfig) -> bool:
    if not seed.question.strip() or not seed.gold_answer.strip():
        return False
    if not seed.supporting_context:
        return False
    ctx = seed.clean_context_text()
    if len(ctx) < cfg.min_context_chars or len(ctx) > cfg.max_context_chars:
        return False
    # Avoid empty / extremely vague answers
    if len(seed.gold_answer.strip()) < 1:
        return False
    return True


def load_hotpot_candidates(cfg: AppConfig, *, rng: random.Random | None = None) -> list[CleanSeed]:
    rng = rng or random.Random(42)
    if cfg.use_fixture_seeds:
        path = Path(cfg.fixture_seeds_path)
        seeds = load_models(path, CleanSeed)
        return seeds[: cfg.candidate_limit]

    from datasets import load_dataset

    # huggingface_hub >=1.x requires namespace/name (bare "hotpot_qa" raises HfUriError)
    ds = load_dataset(cfg.hotpot_dataset, cfg.hotpot_config, split=cfg.hotpot_split)
    indices = list(range(len(ds)))
    rng.shuffle(indices)

    seeds: list[CleanSeed] = []
    yes_no_count = 0
    max_yes_no = int(cfg.candidate_limit * cfg.yes_no_max_fraction)

    for idx in indices:
        if len(seeds) >= cfg.candidate_limit:
            break
        ex = ds[int(idx)]
        answer = str(ex.get("answer") or "").strip()
        question = str(ex.get("question") or "").strip()
        if not answer or not question:
            continue
        if _is_yes_no(answer):
            if yes_no_count >= max_yes_no:
                continue
        supporting, distractors = _build_contexts(ex)
        seed = CleanSeed(
            seed_id=f"hp_{len(seeds) + 1:06d}",
            question=question,
            gold_answer=answer,
            supporting_context=supporting,
            distractor_context=distractors[:8],
            metadata={
                "hotpot_id": ex.get("id"),
                "level": ex.get("level"),
                "type": ex.get("type"),
                "source_index": int(idx),
            },
        )
        if not _candidate_ok(seed, cfg):
            continue
        if _is_yes_no(answer):
            yes_no_count += 1
        seeds.append(seed)
    return seeds


def stage_build_seeds(cfg: AppConfig) -> list[CleanSeed]:
    out = cfg.stage_dir("1_seeds") / "clean_seeds.jsonl"
    if out.exists():
        return load_models(out, CleanSeed)
    if cfg.seed_source == "squad":
        from gurma.seeds.squad import load_squad_candidates

        seeds = load_squad_candidates(cfg)
    else:
        seeds = load_hotpot_candidates(cfg)
    write_jsonl(out, seeds)
    print(f"[P1] wrote {len(seeds)} candidates source={cfg.seed_source} → {out}")
    return seeds
