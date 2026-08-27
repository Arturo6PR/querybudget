# Architecture decisions

## AD-001 — Keep recommendations rule based

Cost governance requires an owner to understand and challenge a finding. Named rules, visible thresholds, and stable fingerprints are more useful here than an unexplained model score.

## AD-002 — Normalize literals before fingerprinting

Daily or account-specific predicates make equivalent query shapes look unique. Normalizing strings, numbers, and whitespace exposes repeated work without retaining literal values.

## AD-003 — Do not add overlapping savings rates

One query can trigger several symptoms of the same underlying scan problem. QueryBudget uses the largest applicable rate per query, while reporting gross rule estimates separately for prioritization.

## AD-004 — Treat enforcement and optimization as separate actions

The analyzer can fail a budget policy, but it never executes or rewrites SQL. Query owners validate correctness and measure the effect before an optimization becomes standard.

