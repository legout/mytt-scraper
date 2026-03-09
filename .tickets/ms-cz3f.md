---
id: ms-cz3f
status: open
deps: [ms-n639, ms-rhk9, ms-a51k]
links: []
created: 2026-03-09T01:22:57Z
type: task
priority: 2
assignee: legout
parent: ms-mvjw
tags: [task, vertical-slice, web, reliability, hitl]
---
# Harden operations: captcha fallback, rate limits, and unified errors

Resolve and implement operational hardening decisions: captcha headed fallback UX, rate limiting thresholds, global error envelope, and thread-safety validation.

## Design

PRD open questions Q2/Q5/Q6 + risks; Spec section 4 and 7.3; Plan P0.8,P1.6,P1.7,P4.1,P4.2

## Acceptance Criteria

- [ ] Captcha detection path offers headed-mode fallback UX
- [ ] Rate limit policy is implemented and verified (429 behavior)
- [ ] Global error handler emits consistent UI-facing error signals
- [ ] Thread-safety findings are documented with concurrency evidence
- [ ] Operational defaults (timeouts/retries/limits) are explicitly recorded

