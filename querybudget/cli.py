from __future__ import annotations

import argparse
import json
from pathlib import Path

from .analyzer import analyze
from .report import write_report
from .scenarios import query_history, team_budgets


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="querybudget")
    subcommands = parser.add_subparsers(dest="command", required=True)
    demo_parser = subcommands.add_parser("demo", help="analyze deterministic warehouse history")
    demo_parser.add_argument("--policy", default="policies/query-policy.json")
    analyze_parser = subcommands.add_parser("analyze", help="analyze JSON query history")
    analyze_parser.add_argument("history")
    analyze_parser.add_argument("budgets")
    analyze_parser.add_argument("--policy", default="policies/query-policy.json")
    analyze_parser.add_argument("--output", default="artifacts/querybudget-report.html")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy = json.loads(Path(args.policy).read_text(encoding="utf-8"))
    if args.command == "demo":
        result = analyze(query_history(), team_budgets(), policy)
        destination = Path("artifacts/querybudget-report.html")
    else:
        history = json.loads(Path(args.history).read_text(encoding="utf-8"))
        budgets = json.loads(Path(args.budgets).read_text(encoding="utf-8"))
        result = analyze(history, budgets, policy)
        destination = Path(args.output)
    result["report"] = str(write_report(result, destination))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 1 if result["summary"]["teams_over_budget"] else 0
