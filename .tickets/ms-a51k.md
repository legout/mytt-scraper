---
id: ms-a51k
status: open
deps: [ms-n639]
links: []
created: 2026-03-09T01:22:57Z
type: feature
priority: 1
assignee: legout
parent: ms-mvjw
tags: [feature, vertical-slice, web, tables]
---
# Implement table browser, table view, and basic query filtering

Add table exploration workflow: list available tables, open a table, render bounded rows, and run simple query/filter operations.

## Design

PRD US-4/US-5; Spec 2.1(table routes),2.2(table signals),3.3; Plan P3.1-P3.5

## Acceptance Criteria

- [ ] /tables shows available tables and row counts
- [ ] /tables/{name} streams selected table metadata and rows via SSE
- [ ] DataTable component renders tabular data safely with row limits
- [ ] Query/filter route updates result set and status signals
- [ ] Invalid table/query failures surface clear error messages

