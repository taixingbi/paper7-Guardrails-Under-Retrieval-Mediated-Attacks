"""Classic prompt-injection detector baseline (external; not GURMA template rules).

Generic heuristics inspired by common PI detectors: ignore/disregard cues,
role-override, delimiter jailbreaks. Distinct from attack-specific operators
in ``gurma.guardrails.rules``.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field

# Broader, published-style PI cues — intentionally NOT the A1/A3/A4 marker strings
_PI_PATTERNS = [
    r"ignore\s+(all\s+)?(previous|prior|above)\s+instructions",
    r"disregard\s+(all\s+)?(previous|prior|above)",
    r"forget\s+(everything|your\s+instructions)",
    r"you\s+are\s+now\s+(dan|jailbroken|unrestricted)",
    r"do\s+not\s+follow\s+(your\s+)?(system|safety)\s+(prompt|policy)",
    r"<\s*/?\s*system\s*>",
    r"\[INST\]",
    r"###\s*(system|instruction)",
    r"begin\s+system\s+prompt",
    r"new\s+instructions?\s*:",
    r"override\s+(the\s+)?(system|user)\s+(message|prompt)",
    r"jailbreak",
    r"developer\s+mode\s+enabled",
]

_PI_RE = [re.compile(p, re.IGNORECASE) for p in _PI_PATTERNS]


@dataclass
class PIHit:
    decision: str  # allow | sanitize | block
    signals: list[str] = field(default_factory=list)
    sanitized_text: str | None = None
    reason: str = ""


def detect_prompt_injection(context: str) -> PIHit:
    """Drop lines matching classic PI cues; block if almost nothing remains."""
    hits = [p.pattern for p in _PI_RE if p.search(context or "")]
    if not hits:
        return PIHit(decision="allow", signals=[], sanitized_text=None, reason="no_pi_hit")

    kept: list[str] = []
    dropped = 0
    for ln in (context or "").splitlines():
        if any(p.search(ln) for p in _PI_RE):
            dropped += 1
            continue
        kept.append(ln)
    sanitized = "\n".join(kept).strip()
    if not sanitized or len(sanitized) < 20:
        return PIHit(
            decision="block",
            signals=["prompt_injection"],
            sanitized_text=None,
            reason=f"pi_block dropped={dropped}",
        )
    return PIHit(
        decision="sanitize",
        signals=["prompt_injection"],
        sanitized_text=sanitized,
        reason=f"pi_sanitize dropped={dropped} patterns={len(hits)}",
    )


def pi_audit_dict(hit: PIHit) -> str:
    return json.dumps(
        {
            "decision": hit.decision,
            "source": "pi_detector",
            "signals": hit.signals,
            "reason": hit.reason,
        }
    )
