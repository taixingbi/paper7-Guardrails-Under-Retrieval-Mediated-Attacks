from __future__ import annotations

import shutil
from pathlib import Path

from gurma.clients.chat import ChatClient
from gurma.concurrent import map_concurrent
from gurma.config import AppConfig
from gurma.eval.aggregate import write_metrics_report
from gurma.eval.pilot_gate import stage_pilot_gate
from gurma.guardrails.llm_guard import InputGuardrail, OutputGuardrail
from gurma.io import load_models, write_jsonl
from gurma.runners.experiment import run_condition
from gurma.schemas.models import AttackCase, RunRecord, ValidatedAttack, ValidatedSeed
from gurma.seeds.hotpot import stage_build_seeds
from gurma.validation.attack import stage_validate_attacks
from gurma.validation.clean import stage_validate_seeds


def _client(cfg: AppConfig) -> ChatClient | None:
    if cfg.skip_llm:
        return None
    return ChatClient(retries=cfg.http_retries)


def _copy_stage(src_root: Path, dst_root: Path, stage: str) -> None:
    src = src_root / stage
    dst = dst_root / stage
    if not src.exists():
        raise FileNotFoundError(f"Missing reuse stage {src}")
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f"[reuse] {src} → {dst}")


def reuse_frozen_stages(cfg: AppConfig) -> tuple[list[ValidatedSeed], list[ValidatedAttack]]:
    """Copy frozen P1–P4 from reuse_from into this run's output_dir."""
    src = cfg.reuse_path
    if src is None:
        raise RuntimeError("reuse_from is not set")
    dst = cfg.output_path
    dst.mkdir(parents=True, exist_ok=True)
    for stage in ("1_seeds", "2_validated_seeds", "3_attacks", "4_validated_attacks"):
        _copy_stage(src, dst, stage)
    seeds = load_models(dst / "2_validated_seeds" / "validated_seeds.jsonl", ValidatedSeed)
    attacks = load_models(
        dst / "4_validated_attacks" / "validated_attacks.jsonl", ValidatedAttack
    )
    if cfg.seed_limit and len(seeds) > cfg.seed_limit:
        keep = {s.seed_id for s in seeds[: cfg.seed_limit]}
        seeds = [s for s in seeds if s.seed_id in keep]
        attacks = [a for a in attacks if a.seed_id in keep]
        write_jsonl(dst / "2_validated_seeds" / "validated_seeds.jsonl", seeds)
        write_jsonl(dst / "4_validated_attacks" / "validated_attacks.jsonl", attacks)
        print(f"[reuse] truncated to seed_limit={cfg.seed_limit}")
    print(
        f"[reuse] frozen seeds={len(seeds)} attacks={len(attacks)} "
        f"guardrail_prompt_version={cfg.guardrail_prompt_version} "
        f"input_mode={cfg.effective_input_mode()}"
    )
    return seeds, attacks


def stage_generate_attacks(cfg: AppConfig, seeds: list[ValidatedSeed]) -> list[AttackCase]:
    from gurma.attacks.adaptive import generate_adaptive_attacks
    from gurma.attacks.heldout import generate_heldout_attacks
    from gurma.attacks.operators import generate_all_attacks

    out = cfg.stage_dir("3_attacks") / "attacks.jsonl"
    if out.exists():
        return load_models(out, AttackCase)
    client = _client(cfg)
    if cfg.attack_family == "held_out":
        attacks = generate_heldout_attacks(seeds, client=client, cfg=cfg)
    elif cfg.attack_family == "adaptive":
        attacks = generate_adaptive_attacks(seeds, client=client, cfg=cfg)
    else:
        attacks = generate_all_attacks(seeds, client=client, cfg=cfg)
    write_jsonl(out, attacks)
    print(f"[P3] wrote {len(attacks)} attacks family={cfg.attack_family} → {out}")
    return attacks


def stage_runs(
    cfg: AppConfig,
    seeds: list[ValidatedSeed],
    attacks: list[ValidatedAttack],
    *,
    force: bool = False,
) -> list[RunRecord]:
    out = cfg.stage_dir("5_runs") / "run_records.jsonl"
    if out.exists() and not force:
        return load_models(out, RunRecord)
    if out.exists() and force:
        out.unlink()
        print(f"[P5] force re-run; removed {out}")

    client = _client(cfg)
    guard_client = client if client is not None else ChatClient.__new__(ChatClient)
    input_guard = InputGuardrail(guard_client, cfg)
    output_guard = OutputGuardrail(guard_client, cfg)

    seed_by_id = {s.seed_id: s for s in seeds}
    models = cfg.answer_model_list()
    jobs: list[tuple[ValidatedSeed, ValidatedAttack | None, str, str]] = []

    if not cfg.skip_clean_runs:
        for seed in seeds:
            for guardrail in cfg.guardrails:
                for model in models:
                    jobs.append((seed, None, guardrail, model))
    for attack in attacks:
        seed = seed_by_id[attack.seed_id]
        for guardrail in cfg.guardrails:
            for model in models:
                jobs.append((seed, attack, guardrail, model))

    def _run(
        job: tuple[ValidatedSeed, ValidatedAttack | None, str, str],
    ) -> RunRecord:
        seed, attack, guardrail, model = job
        return run_condition(
            cfg=cfg,
            client=client,
            input_guard=input_guard,
            output_guard=output_guard,
            seed=seed,
            model=model,
            guardrail=guardrail,
            attack=attack,
        )

    records = map_concurrent(
        jobs,
        _run,
        max_concurrency=cfg.llm_concurrency if not cfg.skip_llm else 8,
        desc="P5 guardrail runs",
    )
    write_jsonl(out, records)
    n_clean = sum(1 for r in records if r.attack_type == "clean")
    n_atk = len(records) - n_clean
    print(
        f"[P5] experimental conditions={len(records)} "
        f"(clean={n_clean}, attack={n_atk}) → {out}"
    )
    print(
        "[P5] note: inference API calls exceed condition count "
        "(input/output guards, judges, validation)."
    )
    return records


def stage_metrics(cfg: AppConfig, records: list[RunRecord] | None = None) -> dict:
    out_dir = cfg.stage_dir("6_metrics")
    out_dir.mkdir(parents=True, exist_ok=True)
    if records is None:
        records = load_models(cfg.stage_dir("5_runs") / "run_records.jsonl", RunRecord)
    records = merge_baseline_g0(cfg, records)
    metrics = write_metrics_report(
        out_dir,
        records,
        bootstrap_n=cfg.bootstrap_n,
        bootstrap_seed=cfg.bootstrap_seed,
    )
    print(f"[P6] wrote metrics → {out_dir}")
    return metrics


def merge_baseline_g0(cfg: AppConfig, records: list[RunRecord]) -> list[RunRecord]:
    """For ablations that only re-run G1/G2, splice in frozen G0 from main."""
    if not cfg.baseline_g0_from:
        return records
    path = Path(cfg.baseline_g0_from)
    if not path.exists():
        raise FileNotFoundError(f"baseline_g0_from missing: {path}")
    base = load_models(path, RunRecord)
    rest = [r for r in records if r.guardrail != "G0"]
    keep_seeds = {r.seed_id for r in rest} or {r.seed_id for r in records}
    keep_models = set(cfg.answer_model_list())
    g0 = [
        r
        for r in base
        if r.guardrail == "G0"
        and r.seed_id in keep_seeds
        and r.model in keep_models
    ]
    print(
        f"[ablation] merged G0={len(g0)} from {path} "
        f"(filtered seeds={len(keep_seeds)} models={sorted(keep_models)}) + new={len(rest)}"
    )
    return g0 + rest


def run_pipeline(cfg: AppConfig) -> None:
    seeds_cand = stage_build_seeds(cfg)
    seeds = stage_validate_seeds(cfg, seeds_cand)
    if not seeds:
        raise RuntimeError(
            "No seeds passed clean freeze gate. "
            "Increase candidate_limit or set clean_pass_mode=either for debugging."
        )
    attacks_raw = stage_generate_attacks(cfg, seeds)
    client = _client(cfg)
    attacks = stage_validate_attacks(cfg, attacks_raw, client=client)
    records = stage_runs(cfg, seeds, attacks)
    stage_metrics(cfg, records)
    stage_pilot_gate(cfg)


def rerun_guardrails(cfg: AppConfig, *, force: bool = True) -> None:
    """Reuse frozen seeds/attacks; re-run P5–P7 with current guardrail_prompt_version."""
    if cfg.reuse_path is None:
        # Same output dir: require existing frozen stages
        seeds_path = cfg.stage_dir("2_validated_seeds") / "validated_seeds.jsonl"
        atk_path = cfg.stage_dir("4_validated_attacks") / "validated_attacks.jsonl"
        if not seeds_path.exists() or not atk_path.exists():
            raise FileNotFoundError(
                "Need reuse_from=... or existing 2_validated_seeds + 4_validated_attacks"
            )
        seeds = load_models(seeds_path, ValidatedSeed)
        attacks = load_models(atk_path, ValidatedAttack)
    else:
        seeds, attacks = reuse_frozen_stages(cfg)

    records = stage_runs(cfg, seeds, attacks, force=force)
    # Persist merged view for gate analysis when G0 is borrowed
    merged = merge_baseline_g0(cfg, records)
    if cfg.baseline_g0_from:
        write_jsonl(cfg.stage_dir("5_runs") / "run_records_with_g0.jsonl", merged)
    stage_metrics(cfg, records)
    # Gate on merged records if available
    if cfg.baseline_g0_from:
        from gurma.eval.pilot_gate import analyze_pilot_gate, collect_samples, summary_markdown
        from gurma.io import write_json
        import json

        summary = analyze_pilot_gate(merged)
        out = cfg.stage_dir("7_ablation")
        out.mkdir(parents=True, exist_ok=True)
        write_json(out / "pilot_gate_summary.json", summary)
        samples = collect_samples(merged)
        with (out / "pilot_gate_samples.jsonl").open("w") as f:
            for row in samples:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
        md = summary_markdown(summary)
        (out / "pilot_gate.md").write_text(md)
        print(md)
        print(f"[P7] wrote pilot gate → {out}")
    else:
        stage_pilot_gate(cfg)


def reuse_frozen_seeds(cfg: AppConfig) -> list[ValidatedSeed]:
    """Copy only frozen seeds (P1–P2). New attacks are generated separately."""
    src = cfg.reuse_path
    if src is None:
        raise RuntimeError("reuse_from is not set")
    dst = cfg.output_path
    dst.mkdir(parents=True, exist_ok=True)
    for stage in ("1_seeds", "2_validated_seeds"):
        _copy_stage(src, dst, stage)
    seeds = load_models(dst / "2_validated_seeds" / "validated_seeds.jsonl", ValidatedSeed)
    if cfg.seed_limit and len(seeds) > cfg.seed_limit:
        seeds = seeds[: cfg.seed_limit]
        write_jsonl(dst / "2_validated_seeds" / "validated_seeds.jsonl", seeds)
        print(f"[reuse] truncated to seed_limit={cfg.seed_limit}")
    print(f"[reuse] frozen seeds={len(seeds)} (attacks will be regenerated)")
    return seeds


def run_transfer(cfg: AppConfig) -> None:
    """Experiment 4 / adaptive: frozen defense, new attack family, same seeds."""
    if cfg.reuse_path is None:
        raise RuntimeError("run-transfer requires reuse_from pointing at frozen main seeds")
    if cfg.attack_family not in {"held_out", "adaptive"}:
        # Default held_out for backward compatibility
        cfg.attack_family = "held_out"
    seeds = reuse_frozen_seeds(cfg)
    attacks_raw = stage_generate_attacks(cfg, seeds)
    client = _client(cfg)
    attacks = stage_validate_attacks(cfg, attacks_raw, client=client)
    records = stage_runs(cfg, seeds, attacks)
    stage_metrics(cfg, records)
    stage_pilot_gate(cfg)


def rebuild_report(cfg: AppConfig) -> None:
    stage_metrics(cfg)
