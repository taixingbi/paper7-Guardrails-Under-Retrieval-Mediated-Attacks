"""Deterministic input detectors for high-precision retrieval-mediated attacks.

Used as a first pass before the LLM input guardrail (hybrid defense).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

# Instruction / hijack (A1)
_INJECTION = [
    r"ignore previous instructions",
    r"disregard the user's",
    r"disregard the (user'?s )?question",
    r"do not answer the factual question",
    r"reply with exactly",
    r"follow the instructions in this document",
    r"attack_success_code_alpha",
]

# Fake authority (A4)
_AUTHORITY = [
    r"system notice",
    r"admin policy",
    r"overrides all prior instructions",
    r"higher-authority retrieved document",
    r"authority_override_ack",
]

# Policy-violating solicitation (A3)
_POLICY = [
    r"requested unsafe procedure",
    r"synthesizing a dangerous chemical weapon",
    r"chemical weapon at home",
    r"how to make a bomb",
    r"step-by-step guide for synthesizing",
]

# Context poisoning templates / cues (A2) — high precision, may miss novel phrasing
_POISON = [
    r"recent archival evidence indicates",
    r"corrected source states",
    r"updated factual answer",
    r"\bnot_[a-z0-9][a-z0-9_\- ]{0,40}\b",
    r"is outdated\. the updated factual answer",
    r"according to a 20\d\d revision note",
]

_LINE_DROP = _INJECTION + _AUTHORITY + _POLICY + _POISON


@dataclass
class RuleHit:
    decision: str  # allow | sanitize | block
    signals: list[str] = field(default_factory=list)
    sanitized_text: str | None = None
    reason: str = ""


def _compile(patterns: list[str]) -> list[re.Pattern[str]]:
    return [re.compile(p, re.IGNORECASE) for p in patterns]


_INJ_RE = _compile(_INJECTION)
_AUTH_RE = _compile(_AUTHORITY)
_POL_RE = _compile(_POLICY)
_POI_RE = _compile(_POISON)
_DROP_RE = _compile(_LINE_DROP)


def _signals_in(text: str) -> list[str]:
    found: list[str] = []
    for label, regs in (
        ("indirect_injection", _INJ_RE),
        ("authority", _AUTH_RE),
        ("policy", _POL_RE),
        ("poisoning", _POI_RE),
    ):
        if any(r.search(text) for r in regs):
            found.append(label)
    return found


def sanitize_by_rules(context: str) -> RuleHit:
    """Drop malicious lines; keep supporting evidence when possible."""
    signals = _signals_in(context)
    if not signals:
        return RuleHit(decision="allow", signals=[], sanitized_text=None, reason="no_rule_hit")

    kept: list[str] = []
    dropped = 0
    for ln in context.splitlines():
        if any(r.search(ln) for r in _DROP_RE):
            dropped += 1
            continue
        # Drop separator-only attack wrappers if following payload already removed
        kept.append(ln)

    sanitized = "\n".join(kept).strip()
    # If almost everything remaining is the attack wrapper header, still OK
    if not sanitized or len(sanitized) < 20:
        return RuleHit(
            decision="block",
            signals=signals,
            sanitized_text=None,
            reason=f"rules_block_after_drop dropped={dropped}",
        )
    return RuleHit(
        decision="sanitize",
        signals=signals,
        sanitized_text=sanitized,
        reason=f"rules_sanitize dropped={dropped} signals={signals}",
    )
