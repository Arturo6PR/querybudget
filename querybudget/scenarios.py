from __future__ import annotations

from typing import Any


def query_history() -> list[dict[str, Any]]:
    return [
        {
            "query_id": "q-001",
            "team": "growth",
            "warehouse": "transform-xl",
            "sql": "SELECT * FROM analytics.events",
            "bytes_scanned": 820_000_000_000,
            "cost_usd": 32.0,
            "cache_hit": False,
        },
        {
            "query_id": "q-002",
            "team": "growth",
            "warehouse": "transform-xl",
            "sql": " select  *  from analytics.events; ",
            "bytes_scanned": 790_000_000_000,
            "cost_usd": 28.0,
            "cache_hit": False,
        },
        {
            "query_id": "q-003",
            "team": "finance",
            "warehouse": "finance-m",
            "sql": "SELECT account_id, SUM(amount) FROM fact_payments WHERE paid_on = '2026-08-25' GROUP BY account_id",
            "bytes_scanned": 90_000_000_000,
            "cost_usd": 14.0,
            "cache_hit": False,
        },
        {
            "query_id": "q-004",
            "team": "finance",
            "warehouse": "finance-m",
            "sql": "SELECT account_id, SUM(amount) FROM fact_payments WHERE paid_on = '2026-08-26' GROUP BY account_id",
            "bytes_scanned": 92_000_000_000,
            "cost_usd": 14.0,
            "cache_hit": False,
        },
        {
            "query_id": "q-005",
            "team": "platform",
            "warehouse": "platform-xs",
            "sql": "SELECT service, error_rate FROM service_hourly WHERE hour >= '2026-08-26'",
            "bytes_scanned": 8_000_000_000,
            "cost_usd": 6.0,
            "cache_hit": True,
        },
        {
            "query_id": "q-006",
            "team": "growth",
            "warehouse": "growth-s",
            "sql": "SELECT campaign_id, conversions FROM campaign_daily WHERE day = '2026-08-26'",
            "bytes_scanned": 12_000_000_000,
            "cost_usd": 8.0,
            "cache_hit": True,
        },
    ]


def team_budgets() -> dict[str, float]:
    return {"growth": 50.0, "finance": 40.0, "platform": 10.0}

