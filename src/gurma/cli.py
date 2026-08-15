from __future__ import annotations

import argparse
from pathlib import Path

from gurma.config import load_config
from gurma.eval.ablation_report import build_ablation_report
from gurma.eval.baseline_compare import build_baseline_compare
from gurma.eval.capacity_compare import build_capacity_compare, build_xfer_size_compare
from gurma.eval.guard_size_compare import build_guard_size_compare
from gurma.eval.paper_report import write_paper_report
from gurma.eval.pilot_gate import stage_pilot_gate
from gurma.pipeline import rebuild_report, rerun_guardrails, run_pipeline, run_transfer


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="gurma",
        description=(
            "Guardrails Under Retrieval-Mediated Attacks "
            "(seed → validate → attack → guardrail eval)"
        ),
    )
    parser.add_argument("-c", "--config", default="configs/smoke.yaml", help="YAML config")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Run P1–P6 pipeline")
    p_run.add_argument(
        "--skip-llm",
        action="store_true",
        help="Offline smoke: fixtures + heuristics (no API calls)",
    )
    sub.add_parser(
        "rebuild-report",
        help="Recompute metrics from saved run_records.jsonl (no LLM)",
    )
    sub.add_parser(
        "pilot-gate",
        help="P7 ablation: G1/G2 decision distributions + rescue (no LLM)",
    )
    p_rerun = sub.add_parser(
        "rerun-guardrails",
        help=(
            "Reuse frozen seeds/attacks (reuse_from or local P1–P4); "
            "force re-run P5–P7 with config guardrail_prompt_version"
        ),
    )
    p_rerun.add_argument(
        "--skip-llm",
        action="store_true",
        help="Offline heuristics only",
    )
    sub.add_parser(
        "ablation-report",
        help="Compare hybrid/rules/llm G1 metrics into data/runs/ablation_compare/",
    )
    sub.add_parser(
        "paper-report",
        help="Generate reports/paper7_results.md from saved metrics JSON (no LLM)",
    )
    p_xfer = sub.add_parser(
        "run-transfer",
        help=(
            "Reuse frozen seeds; generate held_out or adaptive attacks "
            "(set attack_family in config); evaluate frozen G0/G1/G2"
        ),
    )
    p_xfer.add_argument(
        "--skip-llm",
        action="store_true",
        help="Offline heuristics only",
    )
    sub.add_parser(
        "baseline-compare",
        help="Compare hybrid/rules/llm/pi_detector/moderation G1 metrics",
    )
    sub.add_parser(
        "guard-size-compare",
        help="Compare Ministral 3B/8B/14B vs gpt-oss guard LLM (G1, hybrid)",
    )
    sub.add_parser(
        "capacity-compare",
        help="Experiment 6: guard size × (LLM-only|hybrid) G1 grid",
    )
    sub.add_parser(
        "xfer-size-compare",
        help="Guard size × (LLM-only|hybrid) on held-out unseen attacks",
    )

    args = parser.parse_args(argv)
    cfg = (
        load_config(Path(args.config))
        if args.cmd
        not in {
            "ablation-report",
            "paper-report",
            "baseline-compare",
            "guard-size-compare",
            "capacity-compare",
            "xfer-size-compare",
        }
        else None
    )
    if cfg is not None and getattr(args, "skip_llm", False):
        cfg.skip_llm = True

    if args.cmd == "run":
        assert cfg is not None
        run_pipeline(cfg)
    elif args.cmd == "rebuild-report":
        assert cfg is not None
        rebuild_report(cfg)
    elif args.cmd == "pilot-gate":
        assert cfg is not None
        stage_pilot_gate(cfg)
    elif args.cmd == "rerun-guardrails":
        assert cfg is not None
        rerun_guardrails(cfg, force=True)
    elif args.cmd == "ablation-report":
        build_ablation_report()
    elif args.cmd == "baseline-compare":
        build_baseline_compare()
    elif args.cmd == "guard-size-compare":
        build_guard_size_compare()
    elif args.cmd == "capacity-compare":
        build_capacity_compare()
    elif args.cmd == "xfer-size-compare":
        build_xfer_size_compare()
    elif args.cmd == "paper-report":
        write_paper_report()
    elif args.cmd == "run-transfer":
        assert cfg is not None
        run_transfer(cfg)
    else:
        parser.error(f"unknown command {args.cmd}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
