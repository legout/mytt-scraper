# Review: ms-0824

## Critical (must fix)
- None

## Major (should fix)
- `src/mytt_scraper/utils/query_model.py:256-273` – Query validation checks sort columns only against the original schema, so a query that groups and aggregates and then sorts by an aggregation alias (e.g., `avg_ttr`) is rejected even though the column exists in the query output. This causes valid group-by + aggregation + sort queries to fail validation.
  - Source: reviewer-general

- `src/mytt_scraper/utils/query_executor.py:215-254` – `execute_csv` never invokes the validation logic, so `PolarsQueryExecutor(validate=True)` is a no-op for disk-backed tables. Invalid column names only fail when Polars collects, raising `QueryExecutorError` instead of `ValidationError`.
  - Source: reviewer-general, reviewer-second-opinion

## Minor (nice to fix)
- `src/mytt_scraper/utils/query_executor.py:215-253` – The CSV execution path never invokes the schema validation that `execute()` performs, so validation semantics are inconsistent between in-memory and disk-backed code paths.
  - Source: reviewer-general

## Warnings (follow-up ticket)
- None

## Suggestions (follow-up ticket)
- None

## Positive Notes
- The executor makes excellent use of Polars lazy evaluation, applying filters, groupbys, sorts, limits, and offsets without collecting until the end.
- The query model cleanly separates filters, sorts, and aggregations with frozen dataclasses and built-in validation helpers.
- `tests/test_query_executor.py` covers all filter operators, sorting directions, limits/offsets, groupby aggregations, and CSV execution.
- Both in-memory and disk-backed tables are loaded lazily with capped output rows.

## Summary Statistics
- Critical: 0
- Major: 2
- Minor: 1
- Warnings: 0
- Suggestions: 0

## Review Sources
- reviewer-general: review-general.md
- reviewer-spec-audit: review-spec.md
- reviewer-second-opinion: review-second.md
