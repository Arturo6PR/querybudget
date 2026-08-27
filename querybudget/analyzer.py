from __future__ import annotations

import hashlib
import re
from collections import Counter, defaultdict
from typing import Any, Iterable


DEFAULT_POLICY: dict[str, Any] = {
    "unbounded_scan_bytes": 100_000_000_000,
    "high_cost_usd": 10.0,
    "budget_warning_ratio": 0.8,
    "savings_rates": {
        "UNBOUNDED_SCAN": 0.35,
        "REPEATED_QUERY": 0.25,
        "SELECT_STAR": 0.15,
        "HIGH_COST": 0.10,
    },
}


def normalize_sql(sql: str) -> str:
    normalized = sql.lower()
    normalized = re.sub(r"'[^']*'", "?", normalized)
    normalized = re.sub(r"\b\d+(?:\.\d+)?\b", "?", normalized)
    normalized = re.sub(r"\s+", " ", normalized).strip().rstrip(";")
    return normalized


def fingerprint(sql: str) -> str:
    return hashlib.sha256(normalize_sql(sql).encode("utf-8")).hexdigest()[:12]


def validate_record(record: dict[str, Any]) -> None:
    required = {
        "query_id": str,
        "team": str,
        "warehouse": str,
        "sql": str,
        "bytes_scanned": int,
        "cost_usd": (int, float),
        "cache_hit": bool,
    }
    for field, expected in required.items():
        if field not in record:
            raise ValueError(f"missing field: {field}")
        if not isinstance(record[field], expected):
            raise ValueError(f"invalid type: {field}")
    if record["bytes_scanned"] < 0 or record["cost_usd"] < 0:
        raise ValueError("cost and bytes scanned must be non-negative")


def _rules_for(
    record: dict[str, Any], repeated: Counter[str], policy: dict[str, Any]
) -> list[str]:
    sql = normalize_sql(record["sql"])
    rules: list[str] = []
    if re.search(r"\bselect\s+\*", sql):
        rules.append("SELECT_STAR")
    if (
        " where " not in f" {sql} "
        and record["bytes_scanned"] >= policy["unbounded_scan_bytes"]
    ):
        rules.append("UNBOUNDED_SCAN")
    if repeated[fingerprint(record["sql"])] > 1 and not record["cache_hit"]:
        rules.append("REPEATED_QUERY")
    if record["cost_usd"] >= policy["high_cost_usd"]:
        rules.append("HIGH_COST")
    return sorted(rules)


def analyze(
    records: Iterable[dict[str, Any]],
    budgets: dict[str, float],
    policy: dict[str, Any] | None = None,
) -> dict[str, Any]:
    selected_policy = policy or DEFAULT_POLICY
    rows = [dict(record) for record in records]
    for row in rows:
        validate_record(row)
    if len({row["query_id"] for row in rows}) != len(rows):
        raise ValueError("query_id must be unique")

    repeated = Counter(fingerprint(row["sql"]) for row in rows)
    team_cost: dict[str, float] = defaultdict(float)
    findings: list[dict[str, Any]] = []
    rule_savings: dict[str, float] = defaultdict(float)
    for row in sorted(rows, key=lambda item: item["query_id"]):
        team_cost[row["team"]] += float(row["cost_usd"])
        rules = _rules_for(row, repeated, selected_policy)
        rates = [selected_policy["savings_rates"][rule] for rule in rules]
        savings_rate = max(rates, default=0.0)
        estimated_savings = round(float(row["cost_usd"]) * savings_rate, 2)
        if rules:
            for rule in rules:
                rule_savings[rule] += round(
                    float(row["cost_usd"]) * selected_policy["savings_rates"][rule], 2
                )
            findings.append(
                {
                    "query_id": row["query_id"],
                    "team": row["team"],
                    "warehouse": row["warehouse"],
                    "fingerprint": fingerprint(row["sql"]),
                    "rules": rules,
                    "cost_usd": round(float(row["cost_usd"]), 2),
                    "estimated_savings_usd": estimated_savings,
                    "priority": round(estimated_savings * (1 + len(rules) / 10), 2),
                }
            )

    budget_rows = []
    all_teams = sorted(set(budgets) | set(team_cost))
    for team in all_teams:
        actual = round(team_cost.get(team, 0.0), 2)
        limit = round(float(budgets.get(team, 0.0)), 2)
        ratio = actual / limit if limit else float("inf") if actual else 0.0
        if actual > limit:
            status = "OVER"
        elif ratio >= selected_policy["budget_warning_ratio"]:
            status = "WARN"
        else:
            status = "PASS"
        budget_rows.append(
            {
                "team": team,
                "actual_usd": actual,
                "budget_usd": limit,
                "variance_usd": round(limit - actual, 2),
                "utilization_pct": round(ratio * 100, 1) if ratio != float("inf") else None,
                "status": status,
            }
        )

    recommendations = [
        {"rule": rule, "gross_savings_usd": round(value, 2)}
        for rule, value in sorted(rule_savings.items(), key=lambda item: (-item[1], item[0]))
    ]
    total_cost = round(sum(float(row["cost_usd"]) for row in rows), 2)
    potential = round(sum(row["estimated_savings_usd"] for row in findings), 2)
    return {
        "summary": {
            "queries": len(rows),
            "flagged_queries": len(findings),
            "total_cost_usd": total_cost,
            "potential_savings_usd": potential,
            "savings_pct": round((potential / total_cost * 100) if total_cost else 0.0, 1),
            "repeated_fingerprints": sum(count > 1 for count in repeated.values()),
            "teams_over_budget": sum(row["status"] == "OVER" for row in budget_rows),
        },
        "budgets": budget_rows,
        "findings": sorted(findings, key=lambda row: (-row["priority"], row["query_id"])),
        "recommendations": recommendations,
        "policy": selected_policy,
    }

