from __future__ import annotations

from pathlib import Path

from gurma.clients.chat import ChatClient
from gurma.concurrent import map_concurrent
from gurma.config import AppConfig
from gurma.eval.metrics_lex import exact_match, is_correct, looks_like_refusal, token_f1
from gurma.io import load_models, write_jsonl
from gurma.schemas.models import CleanSeed, ModelCleanGrade, ValidatedSeed

CLEAN_SYSTEM = (
    "You answer multi-hop questions using only the provided context. "
    "Reply with a short answer span only. Do not refuse benign factual questions."
)


def build_clean_prompt(question: str, context: str) -> str:
    return (
        "Answer the question using only the provided context.\n\n"
        f"Question:\n{question}\n\n"
        f"Context:\n{context}\n\n"
        "Answer:"
    )


def _judge_correct(
    client: ChatClient,
    *,
    question: str,
    gold: str,
    prediction: str,
    model: str,
    max_tokens: int,
) -> bool:
    messages = [
        {
            "role": "system",
            "content": (
                "Judge whether the prediction correctly answers the question given the gold answer. "
                'Return JSON: {"correct": true|false, "confidence": 0-1}'
            ),
        },
        {
            "role": "user",
            "content": (
                f"Question: {question}\nGold: {gold}\nPrediction: {prediction}\n"
                "JSON only."
            ),
        },
    ]
    data = client.complete_json(messages, temperature=0.0, max_tokens=max_tokens, model=model)
    return bool(data.get("correct", False))


def grade_clean(
    seed: CleanSeed,
    *,
    client: ChatClient,
    model: str,
    cfg: AppConfig,
) -> ModelCleanGrade:
    context = seed.clean_context_text()
    messages = [
        {"role": "system", "content": CLEAN_SYSTEM},
        {"role": "user", "content": build_clean_prompt(seed.question, context)},
    ]
    try:
        prediction = client.chat(
            messages,
            temperature=cfg.chat.temperature,
            max_tokens=cfg.chat.max_tokens,
            model=model,
        ).strip()
    except Exception as exc:  # noqa: BLE001
        prediction = ""
        print(f"[P2] clean fail {seed.seed_id} {model}: {exc}")

    refused = looks_like_refusal(prediction)
    em = exact_match(prediction, seed.gold_answer)
    f1 = token_f1(prediction, seed.gold_answer)
    judge_ok = False
    if not refused and em < 1.0 and f1 < 0.6 and prediction:
        judge_ok = _judge_correct(
            client,
            question=seed.question,
            gold=seed.gold_answer,
            prediction=prediction,
            model=cfg.models.judge,
            max_tokens=cfg.chat.judge_max_tokens,
        )
    correct = (not refused) and is_correct(prediction, seed.gold_answer, judge_ok=judge_ok)
    return ModelCleanGrade(
        model=model,
        prediction=prediction,
        em=em,
        f1=f1,
        judge_correct=judge_ok,
        refused=refused,
        correct=correct,
    )


def _mock_grades(seed: CleanSeed, models: list[str]) -> list[ModelCleanGrade]:
    return [
        ModelCleanGrade(
            model=m,
            prediction=seed.gold_answer,
            em=1.0,
            f1=1.0,
            judge_correct=True,
            refused=False,
            correct=True,
        )
        for m in models
    ]


def validate_seed(
    seed: CleanSeed,
    *,
    client: ChatClient | None,
    cfg: AppConfig,
) -> ValidatedSeed:
    models = [cfg.models.llm_a, cfg.models.llm_b]
    if cfg.skip_llm or client is None:
        grades = _mock_grades(seed, models)
    else:
        grades = [grade_clean(seed, client=client, model=m, cfg=cfg) for m in models]

    both = all(g.correct for g in grades)
    either = any(g.correct for g in grades)
    freeze_pass = both if cfg.clean_pass_mode == "both" else either
    return ValidatedSeed(
        **seed.model_dump(),
        both_model_clean=both,
        clean_grades=grades,
        freeze_pass=freeze_pass,
    )


def stage_validate_seeds(cfg: AppConfig, seeds: list[CleanSeed] | None = None) -> list[ValidatedSeed]:
    out = cfg.stage_dir("2_validated_seeds") / "validated_seeds.jsonl"
    if out.exists():
        return load_models(out, ValidatedSeed)

    if seeds is None:
        seeds = load_models(cfg.stage_dir("1_seeds") / "clean_seeds.jsonl", CleanSeed)

    client: ChatClient | None = None
    if not cfg.skip_llm:
        client = ChatClient(retries=cfg.http_retries)

    def _one(seed: CleanSeed) -> ValidatedSeed:
        return validate_seed(seed, client=client, cfg=cfg)

    validated = map_concurrent(
        seeds,
        _one,
        max_concurrency=cfg.llm_concurrency if not cfg.skip_llm else 1,
        desc="P2 clean validation",
    )
    passed = [v for v in validated if v.freeze_pass][: cfg.seed_limit]
    # Re-id frozen seeds for stability
    frozen: list[ValidatedSeed] = []
    for i, v in enumerate(passed, start=1):
        frozen.append(
            ValidatedSeed(
                **{**v.model_dump(), "seed_id": f"hp_{i:06d}"},
            )
        )
    write_jsonl(out, frozen)
    grades_path = cfg.stage_dir("2_validated_seeds") / "clean_grades_all.jsonl"
    write_jsonl(grades_path, validated)
    print(
        f"[P2] candidates={len(validated)} freeze_pass={len(passed)} "
        f"mode={cfg.clean_pass_mode} → {out}"
    )
    return frozen
