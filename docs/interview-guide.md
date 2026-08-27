# Interview guide

## Two-minute explanation

QueryBudget converts query-history telemetry into an owned, explainable FinOps decision. It normalizes SQL into stable fingerprints, applies named rules, calculates conservative non-additive savings estimates, rolls cost up to team budgets, and returns a blocking exit code when a team exceeds policy.

## Demonstration order

1. Run `python -m querybudget demo` and explain why exit code 1 is expected.
2. Show the two normalized repeated-query groups.
3. Show why query `q-001` has four rules but uses only the 35% savings rate.
4. Open the report and connect Growth's query findings to its over-budget status.
5. Show the optimization playbook and explain the required before/after measurement.

## Tradeoffs to volunteer

- Regex normalization is portable but cannot understand every SQL dialect or query plan.
- Query cost is an allocation signal; it does not measure business value.
- Estimated savings guide investigation and must not be reported as realized savings.
- Team budgets create accountability but need an exception workflow for incident response and planned backfills.

