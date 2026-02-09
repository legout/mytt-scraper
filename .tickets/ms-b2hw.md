---
id: ms-b2hw
status: closed
deps: [ms-ftgp]
links: [ms-ftgp, ms-ekpx]
created: 2026-02-08T17:14:58Z
type: task
priority: 2
assignee: legout
external-ref: seed-add-filters-and-advanced-queries-to-the
tags: [tf, backlog, component:tui, component:viewer, component:query]
---
# Add Textual UI: sort (single column) + groupby aggregation (basic)

## Task

Add UI for sorting and one simple aggregation flow (group by + count/sum/mean) and display results in the DataTable.

## Context

Sorting and simple groupby aggregates cover many user needs (e.g. group by opponent, count matches).

## Acceptance Criteria

- [ ] Sort: select one column + direction
- [ ] Groupby: select 1 column + aggregation type
- [ ] Query runs in a worker; results show in DataTable
- [ ] Works for both in-memory and disk-backed sources

## References

- Seed: seed-add-filters-and-advanced-queries-to-the


## Notes

**2026-02-08T18:09:09Z**

## Implementation Complete

Added UI controls for sorting and groupby aggregation to TablePreviewScreen.

### Changes
- Added sort panel: select column + direction (ASC/DESC)
- Added groupby panel: select column + aggregation (Count/Sum/Mean/Min/Max)
- Combined filter, sort, and groupby into unified query execution
- Background worker keeps UI responsive

### Verification
- Query model tests passed for all combinations (filter only, sort only, groupby, combined)
- Syntax validation passed
- Commit: c5a0840

### Review Summary
- Critical: 0, Major: 0, Minor: 2, Warnings: 0, Suggestions: 3
- No blocking issues found
