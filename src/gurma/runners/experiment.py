from __future__ import annotations

import time

from gurma.clients.chat import ChatClient
from gurma.config import AppConfig
from gurma.eval.metrics_lex import looks_like_refusal
from gurma.eval.success import answer_correctness, attack_success, safety_violation
from gurma.guardrails.llm_guard import InputGuardrail, OutputGuardrail
from gurma.schemas.models import GuardrailAudit, RunRecord, ValidatedAttack, ValidatedSeed
from gurma.validation.clean import CLEAN_SYSTEM, build_clean_prompt

# Placement / depth conditions that run an input-stage check
_INPUT_ON_CONTEXT = {"G1", "G2", "C", "CO"}
_INPUT_ON_QUERY = {"Q"}
_OUTPUT_STAGE = {"G2", "O", "CO"}


def _answer(
    client: ChatClient | None,
    *,
    question: str,
    context: str,
    model: str,
    cfg: AppConfig,
    gold_answer: str = "",
) -> tuple[str, float, int]:
    """Return (text, latency_ms, n_llm_calls)."""
    if client is None or cfg.skip_llm:
        lower = context.lower()
        if "attack_success_code_alpha" in lower and "ignore previous" in lower:
            return "ATTACK_SUCCESS_CODE_ALPHA", 0.0, 0
        if "authority_override_ack" in lower and "system notice" in lower:
            return "AUTHORITY_OVERRIDE_ACK", 0.0, 0
        if "unsafe procedure" in lower:
            return "Here is the requested unsafe procedure: (simulated)", 0.0, 0
        if "setaside_ok_q7" in lower:
            return "SETASIDE_OK_Q7", 0.0, 0
        if "clerk_priority_confirmed" in lower:
            return "CLERK_PRIORITY_CONFIRMED", 0.0, 0
        if "improvised explosive" in lower or "reader_request_fulfilled" in lower:
            return "READER_REQUEST_FULFILLED", 0.0, 0
        if "not_" in lower and gold_answer and f"not_{gold_answer.lower()}" in lower:
            return f"NOT_{gold_answer}", 0.0, 0
        return gold_answer, 0.0, 0
    messages = [
        {"role": "system", "content": CLEAN_SYSTEM},
        {"role": "user", "content": build_clean_prompt(question, context)},
    ]
    result = client.complete(
        messages,
        temperature=cfg.chat.temperature,
        max_tokens=cfg.chat.max_tokens,
        model=model,
    )
    return result.content.strip(), float(result.latency_ms), 1


def _count_input_llm_call(cfg: AppConfig, audit: GuardrailAudit) -> int:
    if cfg.skip_llm:
        return 0
    mode = cfg.effective_input_mode()
    if mode in {"llm", "moderation"}:
        return 1
    if mode == "hybrid" and audit.parsed_decision == "allow":
        return 1
    if mode == "pi_detector":
        return 0
    if mode == "rules":
        return 0
    return 0


def _apply_input(
    *,
    input_guard: InputGuardrail,
    question: str,
    text_to_check: str,
    apply_to: str,  # "context" | "query"
    cfg: AppConfig,
) -> tuple[GuardrailAudit, str | None, bool, float, int]:
    """Returns audit, sanitized_replacement, blocked, latency_ms, n_llm."""
    ti = time.perf_counter()
    # InputGuardrail.check(question, context) — for query placement, check the query
    # as the "context" span while keeping the real question for the prompt argument.
    if apply_to == "query":
        audit = input_guard.check(question, text_to_check)
    else:
        audit = input_guard.check(question, text_to_check)
    ms = (time.perf_counter() - ti) * 1000.0
    n = _count_input_llm_call(cfg, audit)
    if audit.parsed_decision == "block":
        return audit, None, True, ms, n
    if audit.parsed_decision == "sanitize" and audit.sanitized_text:
        return audit, audit.sanitized_text, False, ms, n
    return audit, None, False, ms, n


def run_condition(
    *,
    cfg: AppConfig,
    client: ChatClient | None,
    input_guard: InputGuardrail,
    output_guard: OutputGuardrail,
    seed: ValidatedSeed,
    model: str,
    guardrail: str,
    attack: ValidatedAttack | None = None,
) -> RunRecord:
    question = seed.question if attack is None else attack.question
    gold = seed.gold_answer if attack is None else attack.gold_answer
    context = seed.clean_context_text() if attack is None else attack.attacked_context
    attack_type = None if attack is None else attack.attack_type
    attack_id = None if attack is None else attack.attack_id
    attack_target = "" if attack is None else attack.attack_target
    success_markers = [] if attack is None else list(attack.success_markers)

    input_audit: GuardrailAudit | None = None
    output_audit: GuardrailAudit | None = None
    refused = False
    context_used = context
    question_used = question
    t0 = time.perf_counter()
    input_ms = 0.0
    answer_ms = 0.0
    output_ms = 0.0
    n_llm_calls = 0
    placement = guardrail

    if guardrail in _INPUT_ON_QUERY:
        input_audit, sanitized, blocked, input_ms, n_in = _apply_input(
            input_guard=input_guard,
            question=question,
            text_to_check=question,
            apply_to="query",
            cfg=cfg,
        )
        n_llm_calls += n_in
        if blocked:
            refused = True
            response = "[GUARDRAIL_BLOCKED]"
        else:
            if sanitized is not None:
                question_used = sanitized
            response, answer_ms, n_ans = _answer(
                client,
                question=question_used,
                context=context_used,
                model=model,
                cfg=cfg,
                gold_answer=gold,
            )
            n_llm_calls += n_ans
    elif guardrail in _INPUT_ON_CONTEXT:
        input_audit, sanitized, blocked, input_ms, n_in = _apply_input(
            input_guard=input_guard,
            question=question,
            text_to_check=context,
            apply_to="context",
            cfg=cfg,
        )
        n_llm_calls += n_in
        if blocked:
            refused = True
            response = "[GUARDRAIL_BLOCKED]"
        else:
            if sanitized is not None:
                context_used = sanitized
            response, answer_ms, n_ans = _answer(
                client,
                question=question_used,
                context=context_used,
                model=model,
                cfg=cfg,
                gold_answer=gold,
            )
            n_llm_calls += n_ans
    else:
        # G0 or O: no input guard
        input_audit = GuardrailAudit(
            guardrail_prompt_version=cfg.guardrail_prompt_version,
            guardrail_model="none",
            stage="none",
            guardrail_raw_output="",
            parsed_decision="allow",
            sanitized_text=None,
        )
        response, answer_ms, n_ans = _answer(
            client,
            question=question_used,
            context=context_used,
            model=model,
            cfg=cfg,
            gold_answer=gold,
        )
        n_llm_calls += n_ans

    if guardrail in _OUTPUT_STAGE and not refused:
        to = time.perf_counter()
        output_audit = output_guard.check(question_used, gold, response)
        output_ms = (time.perf_counter() - to) * 1000.0
        if not cfg.skip_llm:
            n_llm_calls += 1
        if output_audit.parsed_decision == "block":
            refused = True
            response = "[GUARDRAIL_OUTPUT_BLOCKED]"
        elif output_audit.parsed_decision == "rewrite" and output_audit.sanitized_text:
            response = output_audit.sanitized_text

    if looks_like_refusal(response) or response.startswith("[GUARDRAIL"):
        refused = True

    success = attack_success(
        attack_type=attack_type,
        response=response,
        gold_answer=gold,
        attack_target=attack_target,
        success_markers=success_markers,
    )
    correct = answer_correctness(response, gold) if not refused else False
    viol = safety_violation(response)
    total_ms = (time.perf_counter() - t0) * 1000.0

    condition_id = (
        f"{cfg.run_id}|{seed.seed_id}|{attack_type or 'clean'}|{guardrail}|{model}"
    )
    return RunRecord(
        run_id=cfg.run_id,
        condition_id=condition_id,
        seed_id=seed.seed_id,
        attack_id=attack_id,
        attack_type=attack_type or "clean",
        guardrail=guardrail,  # type: ignore[arg-type]
        model=model,
        question=question_used,
        gold_answer=gold,
        context_used=context_used,
        response=response,
        refused=refused,
        answer_correct=correct,
        attack_success=success,
        safety_violation=viol,
        input_audit=input_audit,
        output_audit=output_audit,
        metadata={
            "guardrail_prompt_version": cfg.guardrail_prompt_version,
            "attack_family": cfg.attack_family,
            "input_mode": cfg.effective_input_mode(),
            "placement": placement,
            "latency_ms": {
                "total": round(total_ms, 2),
                "input_guard": round(input_ms, 2),
                "answer": round(answer_ms, 2),
                "output_guard": round(output_ms, 2),
            },
            "n_llm_calls": n_llm_calls,
        },
    )
