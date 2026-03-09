---
id: ms-zp93
status: closed
deps: [ms-u51m]
links: []
created: 2026-03-09T01:22:57Z
type: feature
priority: 1
assignee: legout
parent: ms-mvjw
tags: [feature, vertical-slice, web, session]
---
# Implement serializable session state with TTL cleanup

Implement in-memory session model storing serializable data only, cookie persistence helpers, and TTL cleanup.

## Design

PRD 4.3/4.4; Spec 3.4/4.1; Plan P0.6-P0.7

## Acceptance Criteria

- [ ] WebSession excludes non-serializable browser/scraper objects
- [ ] Session helper API supports create/get/update/clear
- [ ] Cookie save/restore recreates scraper state per request
- [ ] TTL cleanup removes expired sessions and enforces max cap
- [ ] Unit tests cover session creation/access/cleanup behavior


## Notes

**2026-03-09T02:15:22Z**

Blocker: Cannot close ticket - implementation incomplete.

**Acceptance Criteria Status:**
- [ ] WebSession excludes non-serializable objects: PARTIAL (dataclass exists but no validation)
- [ ] Session helper API (create/get/update/clear): NOT VERIFIED
- [ ] Cookie save/restore: NOT IMPLEMENTED
- [ ] TTL cleanup with max cap: NOT IMPLEMENTED
- [ ] Unit tests: NOT CREATED (no test_session.py)

**Review/Test Failures:**
- review.md is empty (0 bytes) - no actionable issues documented
- test-results.md missing - tester hit 429 rate limit error
- Post-fix Gate: Uncertain (3 Major issues about missing evidence)

**Required Next Steps:**
1. Re-run implementation to add missing TTL cleanup, cookie helpers
2. Create tests/test_session.py with coverage for session lifecycle
3. Re-run review/test parallel step after rate limit cooldown
4. Verify all acceptance criteria pass before closure

**2026-03-09T02:42:20Z**

Implementation complete:
- WebSession dataclass with serializability validation via __post_init__
- SessionStore with TTL cleanup, max 100 session cap, thread-safe operations
- Cookie persistence helpers (save_cookies/restore_cookies)
- Fixed: constructor validation, atomic lock acquisition for concurrent access
- All 44 unit tests pass
- Commit: 56cd654
