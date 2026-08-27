import unittest

from querybudget.analyzer import analyze, fingerprint, normalize_sql, validate_record
from querybudget.scenarios import query_history, team_budgets


class QueryBudgetTests(unittest.TestCase):
    def test_fingerprint_normalizes_literals_and_formatting(self) -> None:
        first = "SELECT id FROM orders WHERE day = '2026-08-25' AND store_id = 4"
        second = " select id from orders where day = '2026-08-26' and store_id = 9; "
        self.assertEqual(fingerprint(first), fingerprint(second))
        self.assertNotIn("2026", normalize_sql(first))

    def test_demo_finds_budget_and_query_risk(self) -> None:
        result = analyze(query_history(), team_budgets())
        self.assertEqual(result["summary"]["queries"], 6)
        self.assertEqual(result["summary"]["flagged_queries"], 4)
        self.assertEqual(result["summary"]["repeated_fingerprints"], 2)
        self.assertEqual(result["summary"]["teams_over_budget"], 1)
        self.assertEqual(result["summary"]["potential_savings_usd"], 28.0)

    def test_unbounded_select_star_has_traceable_rules(self) -> None:
        result = analyze(query_history(), team_budgets())
        finding = next(row for row in result["findings"] if row["query_id"] == "q-001")
        self.assertIn("SELECT_STAR", finding["rules"])
        self.assertIn("UNBOUNDED_SCAN", finding["rules"])
        self.assertEqual(finding["estimated_savings_usd"], 11.2)

    def test_budget_status_is_owned_by_team(self) -> None:
        result = analyze(query_history(), team_budgets())
        budgets = {row["team"]: row for row in result["budgets"]}
        self.assertEqual(budgets["growth"]["status"], "OVER")
        self.assertEqual(budgets["finance"]["status"], "PASS")
        self.assertEqual(budgets["platform"]["status"], "PASS")

    def test_negative_usage_is_rejected(self) -> None:
        record = query_history()[0].copy()
        record["bytes_scanned"] = -1
        with self.assertRaisesRegex(ValueError, "non-negative"):
            validate_record(record)

    def test_policy_thresholds_are_configurable(self) -> None:
        policy = {
            "unbounded_scan_bytes": 1_000_000_000_000,
            "high_cost_usd": 100.0,
            "budget_warning_ratio": 0.8,
            "savings_rates": {
                "UNBOUNDED_SCAN": 0.35,
                "REPEATED_QUERY": 0.25,
                "SELECT_STAR": 0.15,
                "HIGH_COST": 0.10,
            },
        }
        result = analyze([query_history()[0]], {"growth": 100.0}, policy)
        self.assertEqual(result["findings"][0]["rules"], ["SELECT_STAR"])
        self.assertEqual(result["findings"][0]["estimated_savings_usd"], 4.8)


if __name__ == "__main__":
    unittest.main()
