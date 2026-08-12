from __future__ import annotations

import argparse
from pathlib import Path

from gurma.config import load_config
from gurma.eval.ablation_report import build_ablation_report
from gurma.eval.paper_report import write_paper_report
from gurma.eval.pilot_gate import stage_pilot_gate
from gurma.pipeline import rebuild_report, rerun_guardrails, run_pipeline


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

    args = parser.parse_args(argv)
    cfg = (
        load_config(Path(args.config))
        if args.cmd not in {"ablation-report", "paper-report"}
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
    elif args.cmd == "paper-report":
        write_paper_report()
    else:
        parser.error(f"unknown command {args.cmd}")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
