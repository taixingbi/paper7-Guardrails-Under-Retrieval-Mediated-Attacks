from pathlib import Path

from gurma.config import load_config


def test_config_extends_merges_guard_model(tmp_path: Path):
    base = tmp_path / "base.yaml"
    base.write_text(
        "run_id: base\n"
        "models:\n"
        "  llm_a: nova-pro\n"
        "  guardrail: gpt-oss\n"
        "guardrail_prompt_version: v3\n"
    )
    child = tmp_path / "child.yaml"
    child.write_text(
        "extends: base.yaml\n"
        "run_id: child\n"
        "models:\n"
        "  guardrail: ministral-3b\n"
    )
    cfg = load_config(child)
    assert cfg.run_id == "child"
    assert cfg.models.llm_a == "nova-pro"
    assert cfg.models.guardrail == "ministral-3b"
    assert cfg.guardrail_prompt_version == "v3"


def test_e6_overlay_loads():
    cfg = load_config("configs/main_e6_hybrid_s.yaml")
    assert cfg.run_id == "main_e6_hybrid_s"
    assert cfg.models.guardrail == "ministral-3b"
    assert cfg.models.answer_models == ["nova-pro"]
    assert cfg.guardrail_prompt_version == "v3"
    assert cfg.guardrails == ["G1"]
    assert cfg.chat.guardrail_max_tokens == 768
