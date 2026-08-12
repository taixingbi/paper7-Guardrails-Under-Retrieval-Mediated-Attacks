from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import yaml
from pydantic import BaseModel, Field


class ChatConfig(BaseModel):
    temperature: float = 0.0
    max_tokens: int = 512
    judge_max_tokens: int = 256
    guardrail_max_tokens: int = 512


class ModelsConfig(BaseModel):
    llm_a: str = "nova-pro"
    llm_b: str = "llama"
    guardrail: str = "gpt-oss"
    judge: str = "gpt-oss"


class AppConfig(BaseModel):
    run_id: str = "smoke"
    output_dir: str = "data/runs/smoke"
    seed_limit: int = 20
    candidate_limit: int = 60
    # both = freeze requires both models correct (reported tables)
    # either = debug candidate yield only
    clean_pass_mode: Literal["both", "either"] = "both"
    models: ModelsConfig = Field(default_factory=ModelsConfig)
    guardrail_prompt_version: str = "v1"
    guardrails: list[str] = Field(default_factory=lambda: ["G0", "G1", "G2"])
    attacks: list[str] = Field(
        default_factory=lambda: [
            "indirect_injection",
            "context_poisoning",
            "policy_retrieval",
            "authority_conflict",
        ]
    )
    chat: ChatConfig = Field(default_factory=ChatConfig)
    llm_concurrency: int = 4
    http_retries: int = 5
    hotpot_dataset: str = "hotpotqa/hotpot_qa"
    hotpot_split: str = "validation"
    hotpot_config: str = "distractor"
    skip_llm: bool = False
    use_fixture_seeds: bool = False
    fixture_seeds_path: str = "data/fixtures/fixture_seeds.jsonl"
    reuse_from: str | None = None
    # Legacy flag; prefer input_guardrail_mode
    input_hybrid: bool = False
    # hybrid = rules then LLM; rules = rules only; llm = LLM only
    input_guardrail_mode: Literal["hybrid", "rules", "llm"] | None = None
    # Merge G0 rows from a completed run into metrics (ablation: only re-run G1/G2)
    baseline_g0_from: str | None = None
    yes_no_max_fraction: float = 0.15
    max_context_chars: int = 12000
    min_context_chars: int = 200

    @property
    def output_path(self) -> Path:
        return Path(self.output_dir)

    @property
    def reuse_path(self) -> Path | None:
        return Path(self.reuse_from) if self.reuse_from else None

    def effective_input_mode(self) -> Literal["hybrid", "rules", "llm"]:
        if self.input_guardrail_mode is not None:
            return self.input_guardrail_mode
        return "hybrid" if self.input_hybrid else "llm"

    def stage_dir(self, name: str) -> Path:
        return self.output_path / name


def load_config(path: str | Path) -> AppConfig:
    data: dict[str, Any] = yaml.safe_load(Path(path).read_text()) or {}
    return AppConfig.model_validate(data)
