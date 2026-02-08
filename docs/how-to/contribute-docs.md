# Contribute to Documentation

This guide shows you how to set up a local documentation environment, preview your changes, and follow the project's documentation conventions.

## Prerequisites

Ensure you have the project dependencies installed:

```bash
uv sync
```

This installs all required packages including Zensical, the documentation generator used by this project.

## Preview Documentation Locally

Run the Zensical development server with hot reload:

```bash
uv run zensical serve
```

The site will be available at `http://localhost:8080` (or another port if 8080 is in use).

Changes to markdown files are automatically reflected in the browser—no need to restart the server.

## Build Documentation

To build the static site for production:

```bash
uv run zensical build
```

The built site is output to the `site/` directory. You can verify the build locally by opening `site/index.html` in a browser.

## Where to Add New Pages

We follow the [Diátaxis](https://diataxis.fr/) documentation framework. Choose the appropriate section based on your content:

| Section | Use For | Location |
|---------|---------|----------|
| **Tutorials** | Learning-oriented, step-by-step lessons | `docs/tutorials/` |
| **How-To Guides** | Task-oriented problem solving | `docs/how-to/` |
| **Reference** | Technical details, API docs | `docs/reference/` |
| **Explanation** | Concepts, background knowledge | `docs/explanation/` |

## File Naming Conventions

- Use **kebab-case** (lowercase with hyphens): `my-guide-name.md`
- Be descriptive but concise
- Use action verbs for how-to guides: `search-players.md`, `export-data.md`

## Adding a New Page

1. **Create the file** in the appropriate section directory
2. **Add to navigation** in `zensical.toml` under the relevant `[nav]` section
3. **Link from the section index** (e.g., `docs/how-to/index.md`)

### Example: Adding a How-To Guide

1. Create `docs/how-to/my-new-guide.md`
2. Add to `zensical.toml`:
   ```toml
   [nav."How-To Guides"]
   "My New Guide" = "docs/how-to/my-new-guide.md"
   ```
3. Add a link in `docs/how-to/index.md`

## Style Guidelines

- Use clear, concise language
- Include code examples where appropriate
- Cross-reference related documentation using relative links: `[link text](path/to/file.md)`
- Follow existing file naming conventions (kebab-case)

## Checking Your Changes

Before submitting:

1. Preview locally with `uv run zensical serve`
2. Build with `uv run zensical build` to ensure no errors
3. Verify all internal links work
4. Check that new pages appear in navigation
