"""Lexical answer metrics (SQuAD-style EM / token F1)."""

from __future__ import annotations

import re
import string
from collections import Counter

_ARTICLES_RE = re.compile(r"\b(a|an|the)\b", re.IGNORECASE)
_PUNCT_TABLE = str.maketrans("", "", string.punctuation)
_WS_RE = re.compile(r"\s+")

_REFUSAL_MARKERS = (
    "i cannot",
    "i can't",
    "i'm unable",
    "i am unable",
    "as an ai",
    "i must refuse",
    "cannot assist",
    "can't assist",
    "unable to answer",
    "will not answer",
    "refuse to",
    "sorry, but i",
)


def normalize_answer(text: str) -> str:
    if text is None:
        return ""
    s = text.lower()
    s = s.translate(_PUNCT_TABLE)
    s = _ARTICLES_RE.sub(" ", s)
    s = _WS_RE.sub(" ", s).strip()
    return s


def exact_match(prediction: str, gold: str) -> float:
    return 1.0 if normalize_answer(prediction) == normalize_answer(gold) else 0.0


def token_f1(prediction: str, gold: str) -> float:
    pred_tokens = normalize_answer(prediction).split()
    gold_tokens = normalize_answer(gold).split()
    if not pred_tokens and not gold_tokens:
        return 1.0
    if not pred_tokens or not gold_tokens:
        return 0.0
    common = Counter(pred_tokens) & Counter(gold_tokens)
    num_same = sum(common.values())
    if num_same == 0:
        return 0.0
    precision = num_same / len(pred_tokens)
    recall = num_same / len(gold_tokens)
    return 2 * precision * recall / (precision + recall)


def contains_answer(text: str, answer: str) -> bool:
    return normalize_answer(answer) in normalize_answer(text)


def looks_like_refusal(text: str) -> bool:
    s = (text or "").lower().strip()
    if not s:
        return True
    return any(m in s for m in _REFUSAL_MARKERS)


def is_correct(prediction: str, gold: str, *, f1_threshold: float = 0.6, judge_ok: bool = False) -> bool:
    return bool(exact_match(prediction, gold) >= 1.0 or token_f1(prediction, gold) >= f1_threshold or judge_ok)
