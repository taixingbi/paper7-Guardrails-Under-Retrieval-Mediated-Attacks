from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import httpx
from dotenv import load_dotenv

from gurma.clients.http_retry import request_with_retry


@dataclass
class ChatResult:
    content: str
    finish_reason: str | None = None
    usage: dict[str, Any] = field(default_factory=dict)
    raw_message: dict[str, Any] = field(default_factory=dict)
    truncated: bool = False
    model: str = ""

    @property
    def text(self) -> str:
        return self.content


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts: list[str] = []
        for item in value:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict):
                typ = str(item.get("type") or "")
                if typ in {"reasoning", "thinking"}:
                    continue
                if "text" in item and item["text"] is not None:
                    parts.append(str(item["text"]))
                elif "content" in item and isinstance(item["content"], str):
                    parts.append(item["content"])
        return "".join(parts)
    return str(value)


def extract_message_content(message: dict[str, Any]) -> str:
    for key in ("content", "output_text", "answer", "final_answer"):
        text = _as_text(message.get(key)).strip()
        if text:
            return text
    for key in ("response", "output"):
        nested = message.get(key)
        if isinstance(nested, dict):
            text = extract_message_content(nested).strip()
            if text:
                return text
        text = _as_text(nested).strip()
        if text:
            return text
    return ""


def is_truncated_completion(
    *,
    finish_reason: str | None,
    usage: dict[str, Any],
    max_tokens: int,
    content: str,
) -> bool:
    fr = (finish_reason or "").lower()
    if fr in {"length", "max_tokens", "max_length"}:
        return True
    completion_tokens = usage.get("completion_tokens") or usage.get("output_tokens")
    if isinstance(completion_tokens, int) and max_tokens > 0 and completion_tokens >= max_tokens:
        return True
    s = content.strip()
    if s.startswith("{") and not s.endswith("}"):
        return True
    if s.startswith("[") and not s.endswith("]"):
        return True
    if s.count("{") > s.count("}"):
        return True
    return False


class ChatClient:
    """OpenAI-compatible chat client for Bedrock inference MVP."""

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        model: str | None = None,
        timeout: float = 180.0,
        *,
        retries: int = 5,
    ) -> None:
        load_dotenv()
        self.base_url = (base_url or os.getenv("GURMA_INFERENCE_URL") or "").rstrip("/")
        self.api_key = api_key or os.getenv("GURMA_INFERENCE_API_KEY") or "1234"
        self.model = model or os.getenv("GURMA_INFERENCE_MODEL") or "nova-pro"
        self.timeout = timeout
        self.retries = max(0, int(retries))
        if not self.base_url:
            raise RuntimeError(
                "GURMA_INFERENCE_URL is not set. Copy .env.example → .env (see example.md)."
            )

    def complete(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        model: str | None = None,
    ) -> ChatResult:
        url = f"{self.base_url}/v1/chat/completions".replace("//v1/", "/v1/")
        used_model = model or self.model
        payload: dict[str, Any] = {
            "model": used_model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        def _once() -> dict[str, Any]:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, headers=headers, json=payload)
                resp.raise_for_status()
                return resp.json()

        data = request_with_retry(_once, retries=self.retries, label="chat")
        if data.get("error"):
            raise RuntimeError(f"chat error: {data.get('error')} {data.get('detail')}")
        choice = (data.get("choices") or [{}])[0]
        message = choice.get("message") or {}
        if not isinstance(message, dict):
            message = {}
        content = extract_message_content(message)
        finish_reason = choice.get("finish_reason")
        usage = data.get("usage") or {}
        if not isinstance(usage, dict):
            usage = {}
        truncated = is_truncated_completion(
            finish_reason=finish_reason,
            usage=usage,
            max_tokens=max_tokens,
            content=content,
        )
        return ChatResult(
            content=content,
            finish_reason=str(finish_reason) if finish_reason is not None else None,
            usage=usage,
            raw_message=message,
            truncated=truncated,
            model=used_model,
        )

    def chat(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 1024,
        model: str | None = None,
    ) -> str:
        return self.complete(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        ).content

    def complete_json(
        self,
        messages: list[dict[str, str]],
        *,
        temperature: float = 0.0,
        max_tokens: int = 512,
        model: str | None = None,
    ) -> dict[str, Any]:
        from gurma.clients.json_parse import parse_json_object

        text = self.chat(
            messages,
            temperature=temperature,
            max_tokens=max_tokens,
            model=model,
        )
        return parse_json_object(text)