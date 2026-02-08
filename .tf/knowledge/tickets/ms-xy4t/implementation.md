# Implementation: ms-xy4t

## Summary
Created a contributor-focused documentation page describing how to preview/build docs locally and basic style rules.

## Files Changed
- `docs/how-to/contribute-docs.md` (created) - New how-to guide for documentation contributors
- `zensical.toml` (modified) - Added "Contribute to Documentation" to How-To Guides navigation
- `docs/how-to/index.md` (modified) - Added link to new guide under "Contributing" section

## Key Decisions
- Placed the guide in `docs/how-to/` since it's task-oriented (how to contribute to docs)
- Used "Contribute to Documentation" as the nav title to match the action-oriented style of other how-to guides
- Included all required sections from the acceptance criteria:
  - Prerequisites (uv sync)
  - Preview (`uv run zensical serve`)
  - Build (`uv run zensical build`)
  - Naming conventions (kebab-case)
  - Where to add new pages (Diátaxis framework sections)

## Tests Run
- `uv run zensical build` - Build succeeded, new page appears in output

## Verification
- Documentation builds without errors
- New page is accessible at `/how-to/contribute-docs/` in the built site
- Navigation updated in zensical.toml
- Index page links to new guide
