from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

AttackType = Literal[
    "indirect_injection",
    "context_poisoning",
    "policy_retrieval",
    "authority_conflict",
]

GuardrailId = Literal["G0", "G1", "G2"]
InputDecision = Literal["allow", "sanitize", "block"]
OutputDecision = Literal["pass", "rewrite", "block"]


class CleanSeed(BaseModel):
    schema_version: str = "1.0"
    seed_id: str
    question: str
    gold_answer: str
    supporting_context: list[str]
    distractor_context: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    def clean_context_text(self) -> str:
        parts = list(self.supporting_context) + list(self.distractor_context)
        return "\n\n".join(p.strip() for p in parts if p and p.strip())


class ModelCleanGrade(BaseModel):
    model: str
    prediction: str
    em: float
    f1: float
    judge_correct: bool
    refused: bool
    correct: bool


class ValidatedSeed(CleanSeed):
    both_model_clean: bool = False
    clean_grades: list[ModelCleanGrade] = Field(default_factory=list)
    freeze_pass: bool = False


class AttackCase(BaseModel):
    schema_version: str = "1.0"
    attack_id: str
    seed_id: str
    attack_type: AttackType
    question: str
    gold_answer: str
    clean_context: str
    attacked_context: str
    attack_payload: str
    attack_target: str
    success_markers: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class AttackValidation(BaseModel):
    """Acceptance is semantic_valid AND payload_present only.

    baseline_effect is annotation/characterization — never an acceptance gate.
    """

    schema_version: str = "1.0"
    attack_id: str
    seed_id: str
    attack_type: AttackType
    semantic_valid: bool
    payload_present: bool
    accepted: bool
    baseline_effect: bool | None = None
    baseline_effect_notes: dict[str, Any] = Field(default_factory=dict)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @classmethod
    def from_checks(
        cls,
        *,
        attack_id: str,
        seed_id: str,
        attack_type: AttackType,
        semantic_valid: bool,
        payload_present: bool,
        baseline_effect: bool | None = None,
        baseline_effect_notes: dict[str, Any] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> AttackValidation:
        return cls(
            attack_id=attack_id,
            seed_id=seed_id,
            attack_type=attack_type,
            semantic_valid=semantic_valid,
            payload_present=payload_present,
            accepted=bool(semantic_valid and payload_present),
            baseline_effect=baseline_effect,
            baseline_effect_notes=baseline_effect_notes or {},
            metadata=metadata or {},
        )


class ValidatedAttack(AttackCase):
    semantic_valid: bool = True
    payload_present: bool = True
    accepted: bool = True
    baseline_effect: bool | None = None
    baseline_effect_notes: dict[str, Any] = Field(default_factory=dict)


class GuardrailAudit(BaseModel):
    guardrail_prompt_version: str
    guardrail_model: str
    stage: Literal["input", "output", "none"]
    guardrail_raw_output: str = ""
    parsed_decision: str = "allow"
    sanitized_text: str | None = None


class RunRecord(BaseModel):
    schema_version: str = "1.0"
    run_id: str
    condition_id: str
    seed_id: str
    attack_id: str | None = None
    attack_type: str | None = None  # None / "clean"
    guardrail: GuardrailId
    model: str
    question: str
    gold_answer: str
    context_used: str
    response: str
    refused: bool = False
    answer_correct: bool | None = None
    attack_success: bool | None = None
    safety_violation: bool = False
    input_audit: GuardrailAudit | None = None
    output_audit: GuardrailAudit | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
