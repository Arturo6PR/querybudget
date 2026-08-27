# Optimization playbook

## UNBOUNDED_SCAN

Confirm whether a partition predicate is semantically valid. Measure bytes scanned before and after. Do not add a date filter that silently changes the required business population.

## REPEATED_QUERY

Identify whether repetition should be solved by result caching, a persisted intermediate model, or a semantic-layer aggregate. Verify freshness expectations before sharing results.

## SELECT_STAR

Project only required columns and measure scan reduction. Keep schema-change behavior explicit: broad projections sometimes exist to absorb new fields, which may be an intentional contract.

## HIGH_COST

Inspect the query plan rather than assuming cost alone indicates waste. Large, valuable workloads can be efficient. Prioritize cost multiplied by an evidence-backed savings opportunity.

## Validation record

For every accepted recommendation, retain the original fingerprint, owner, before/after bytes, before/after cost, runtime, result-count comparison, and rollback decision.

