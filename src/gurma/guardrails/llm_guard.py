from __future__ import annotations

import json
from pathlib import Path

from gurma.clients.chat import ChatClient
from gurma.clients.json_parse import parse_json_object
from gurma.config import AppConfig
from gurma.guardrails.pi_detector import detect_prompt_injection, pi_audit_dict
from gurma.guardrails.rules import sanitize_by_rules
from gurma.schemas.models import GuardrailAudit

_REPO_ROOT = Path(__file__).resolve().parents[3]


def prompt_path(version: str, stage: str) -> Path:
    return _REPO_ROOT / "prompts" / "guardrails" / f"{stage}_{version}.txt"


def load_prompt(version: str, stage: str) -> str:
    path = prompt_path(version, stage)
    if not path.exists():
        raise FileNotFoundError(f"Missing guardrail prompt: {path}")
    return path.read_text().strip()


def _audit_from_rules(version: str, context: str, *, model_label: str) -> GuardrailAudit:
    hit = sanitize_by_rules(context)
    if hit.decision == "allow":
        return GuardrailAudit(
            guardrail_prompt_version=version,
            guardrail_model=model_label,
            stage="input",
            guardrail_raw_output=json.dumps(
                {"decision": "allow", "source": "rules", "signals": []}
            ),
            parsed_decision="allow",
            sanitized_text=None,
        )
    return GuardrailAudit(
        guardrail_prompt_version=version,
        guardrail_model=model_label,
        stage="input",
        guardrail_raw_output=json.dumps(
            {
                "decision": hit.decision,
                "source": "rules",
                "signals": hit.signals,
                "reason": hit.reason,
            }
        ),
        parsed_decision=hit.decision,
        sanitized_text=hit.sanitized_text,
    )


def _audit_from_pi(version: str, context: str) -> GuardrailAudit:
    hit = detect_prompt_injection(context)
    return GuardrailAudit(
        guardrail_prompt_version=version,
        guardrail_model="pi_detector",
        stage="input",
        guardrail_raw_output=pi_audit_dict(hit),
        parsed_decision=hit.decision,
        sanitized_text=hit.sanitized_text,
    )


class InputGuardrail:
    def __init__(self, client: ChatClient, cfg: AppConfig) -> None:
        self.client = client
        self.cfg = cfg
        self.version = cfg.guardrail_prompt_version
        self.model = cfg.models.guardrail
        self.mode = cfg.effective_input_mode()
        if self.mode == "moderation":
            self.system = load_prompt("v1", "moderation")
            self.version_label = "moderation_v1"
        else:
            self.system = load_prompt(self.version, "input")
            self.version_label = self.version

    def check(self, question: str, context: str) -> GuardrailAudit:
        if self.mode == "pi_detector":
            return _audit_from_pi(self.version_label, context)

        if self.cfg.skip_llm:
            if self.mode == "moderation":
                # Offline: fall back to classic PI detector for moderation baseline
                return _audit_from_pi("moderation_v1_heuristic", context)
            return _audit_from_rules(self.version, context, model_label="heuristic")

        if self.mode in {"rules", "hybrid"}:
            rules_audit = _audit_from_rules(
                self.version,
                context,
                model_label="rules" if self.mode == "rules" else f"rules+{self.model}",
            )
            if self.mode == "rules":
                return rules_audit
            if rules_audit.parsed_decision != "allow":
                return rules_audit

        # LLM residual (hybrid allow), LLM-only, or external moderation
        user = (
            f"Question:\n{question}\n\nRetrieved context:\n{context}\n\n"
            "Return JSON decision."
        )
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user},
        ]
        raw = ""
        try:
            result = self.client.complete(
                messages,
                temperature=0.0,
                max_tokens=self.cfg.chat.guardrail_max_tokens,
                model=self.model,
            )
            raw = result.content
            data = parse_json_object(raw)
        except Exception as exc:  # noqa: BLE001
            raw = str(exc)
            data = {"decision": "allow", "reason": "guardrail_error"}

        decision = str(data.get("decision") or "allow").lower()
        if decision not in {"allow", "sanitize", "block"}:
            decision = "allow"
        sanitized = data.get("sanitized_context") or data.get("sanitized_text")
        sanitized_text = str(sanitized).strip() if sanitized else None
        if decision == "sanitize" and not sanitized_text:
            decision = "block"
        return GuardrailAudit(
            guardrail_prompt_version=self.version_label,
            guardrail_model=(
                f"moderation:{self.model}" if self.mode == "moderation" else self.model
            ),
            stage="input",
            guardrail_raw_output=raw or str(data),
            parsed_decision=decision,
            sanitized_text=sanitized_text,
        )


class OutputGuardrail:
    def __init__(self, client: ChatClient, cfg: AppConfig) -> None:
        self.client = client
        self.cfg = cfg
        self.version = cfg.guardrail_prompt_version
        self.system = load_prompt(self.version, "output")
        self.model = cfg.models.guardrail

    def check(self, question: str, gold_answer: str, response: str) -> GuardrailAudit:
        if self.cfg.skip_llm:
            lowered = response.lower()
            if any(
                m in lowered
                for m in (
                    "attack_success_code_alpha",
                    "authority_override_ack",
                    "requested unsafe procedure",
                    "chemical weapon",
                )
            ):
                return GuardrailAudit(
                    guardrail_prompt_version=self.version,
                    guardrail_model="heuristic",
                    stage="output",
                    guardrail_raw_output='{"decision":"block"}',
                    parsed_decision="block",
                    sanitized_text=None,
                )
            return GuardrailAudit(
                guardrail_prompt_version=self.version,
                guardrail_model="heuristic",
                stage="output",
                guardrail_raw_output='{"decision":"pass"}',
                parsed_decision="pass",
                sanitized_text=None,
            )

        user = (
            f"Question:\n{question}\n"
            f"Gold answer (for task reference):\n{gold_answer}\n"
            f"Model response:\n{response}\n"
            "Return JSON decision."
        )
        messages = [
            {"role": "system", "content": self.system},
            {"role": "user", "content": user},
        ]
        raw = ""
        try:
            result = self.client.complete(
                messages,
                temperature=0.0,
                max_tokens=self.cfg.chat.guardrail_max_tokens,
                model=self.model,
            )
            raw = result.content
            data = parse_json_object(raw)
        except Exception as exc:  # noqa: BLE001
            raw = str(exc)
            data = {"decision": "pass", "reason": "guardrail_error"}

        decision = str(data.get("decision") or "pass").lower()
        if decision not in {"pass", "rewrite", "block"}:
            decision = "pass"
        rewrite = data.get("rewrite_text")
        sanitized_text = str(rewrite).strip() if rewrite else None
        return GuardrailAudit(
            guardrail_prompt_version=self.version,
            guardrail_model=self.model,
            stage="output",
            guardrail_raw_output=raw or str(data),
            parsed_decision=decision,
            sanitized_text=sanitized_text,
        )
