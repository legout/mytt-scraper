<!-- PI-TK-FLOW:START -->
## pi-tk-flow operating model
- `PROJECT.md` is the canonical source for project/product/system context.
- `tf-*` refers to pi-tk-flow prompts, agents, and workflow commands.
- `tk` refers to the external ticket CLI only.
- Legacy `tk-*` pi commands/agents should not be used for new work.

## Read order
Before non-trivial work, read in this order:
1. `AGENTS.md`
2. `PROJECT.md`
3. relevant architecture/stack docs and referenced project docs
4. relevant `.tf/knowledge/...`
5. relevant `.tf/plans/...` and `.tickets/...` when doing planned or ticketed work
6. transient `.subagent-runs/...` artifacts only for the current run

## Command boundary
- Use `/tf-bootstrap` to install/update shipped pi-tk-flow templates.
- Use `/tf-init` to initialize project context for pi-tk-flow adoption.
- Use `/tf-brainstorm`, `/tf-plan`, `/tf-plan-check`, `/tf-plan-refine`, `/tf-ticketize`, `/tf-implement`, `/tf-refactor`, and `/tf-simplify` for workflow execution.
- Use `tk` for ticket operations: `tk ready`, `tk show`, `tk add-note`, `tk status`, `tk close`, etc.

## Knowledge rules
- Keep durable reusable knowledge under `.tf/knowledge/...`.
- Keep transient runtime artifacts under `.subagent-runs/...` only.
- Prefer topic directories such as `.tf/knowledge/topics/<topic-slug>/summary.md`, `research.md`, and `library-research.md`.
- Use baseline files under `.tf/knowledge/baselines/` for coding standards, testing expectations, and architecture reference material.

## Guardrails
- Do not treat `.subagent-runs/...` as durable truth.
- Do not mix the `tf-*` workflow surface with the `tk` ticket CLI.
- Update `PROJECT.md` and `.tf/knowledge/baselines/...` when durable project understanding changes materially.
<!-- PI-TK-FLOW:END -->

## Project-specific guidance

### Quick Commands
- run: `uv run python`
- test: `uv run pytest`
- lint: `uv run ruff check .`
- format: `uv run ruff format .`
- typecheck: `uv run mypy .`

### Stack Notes
- Python 3.13+ with uv package management
- Playwright for browser automation
- Textual for TUI
- Polars/Pandas/PyArrow for data processing
- DuckDB for in-memory SQL queries

### Conventions
- See [Coding Standards](.tf/knowledge/baselines/coding-standards.md)
- See [Testing](.tf/knowledge/baselines/testing.md)
- See [Architecture](.tf/knowledge/baselines/architecture.md)

### Critical Constraints
- **Never store credentials** - session-only auth
- **Respect rate limits** - delays between requests
- **Fragile selectors** - DOM-dependent scraping may break on site updates
