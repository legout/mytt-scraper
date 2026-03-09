Done. I've created the anchor-context.md file with:

- **Ticket Summary**: Login/logout flow and protected route enforcement for the web UI
- **Complexity Assessment**: Medium level (~150-250 LOC) - session state already exists, main work is route handlers + SSE
- **Research Gaps**: StarHTML SSE patterns, protected route guards, asyncio.to_thread() integration
- **External Libraries**: starhtml (web framework), playwright (login), asyncio (threading)
- **Testing Requirements**: New `tests/test_auth_routes.py` with patterns from existing `test_session.py`
- **Recommended Path**: B (Standard) - straightforward auth flow
- **Concrete File Hints**: Starting points include:
  - `src/mytt_scraper/web/routes/auth.py` (stub to implement)
  - `src/mytt_scraper/utils/auth.py::login()` (existing login to wrap)
  - `src/mytt_scraper/web/state.py` (session store from ms-zp93)