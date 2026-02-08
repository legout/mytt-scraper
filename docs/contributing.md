# Contributing to Documentation

This guide explains how to work with the mytt-scraper documentation.

## Documentation Structure

We follow the [Diátaxis](https://diataxis.fr/) documentation framework, organizing content into four sections:

| Section | Purpose | Location |
|---------|---------|----------|
| **Tutorials** | Learning-oriented, step-by-step lessons | `docs/tutorials/` |
| **How-To Guides** | Task-oriented, problem-solving | `docs/how-to/` |
| **Reference** | Information-oriented, technical details | `docs/reference/` |
| **Explanation** | Understanding-oriented, concepts | `docs/explanation/` |

## Local Development

### Prerequisites

Ensure you have the project dependencies installed:

```bash
uv sync
```

### Preview Documentation

Run the Zensical development server with hot reload:

```bash
uv run zensical serve
```

The site will be available at `http://localhost:8080` (or another port if 8080 is in use).

Changes to markdown files are automatically reflected in the browser.

### Build Documentation

To build the static site for production:

```bash
uv run zensical build
```

The built site is output to the `site/` directory.

## Adding New Documentation

### Adding a Tutorial

1. Create a new file in `docs/tutorials/`
2. Add it to the nav in `zensical.toml` under `[nav.Tutorials]`
3. Link to it from `docs/tutorials/index.md`

### Adding a How-To Guide

1. Create a new file in `docs/how-to/`
2. Add it to the nav in `zensical.toml` under `[nav."How-To Guides"]`
3. Link to it from `docs/how-to/index.md`

### Adding Reference Documentation

1. Create a new file in `docs/reference/`
2. Add it to the nav in `zensical.toml` under `[nav.Reference]`
3. Link to it from `docs/reference/index.md`

### Adding an Explanation

1. Create a new file in `docs/explanation/`
2. Add it to the nav in `zensical.toml` under `[nav.Explanation]`
3. Link to it from `docs/explanation/index.md`

## Navigation Configuration

The site navigation is defined in `zensical.toml` at the project root. When adding new pages, update the `[nav]` sections accordingly.

## Style Guidelines

- Use clear, concise language
- Include code examples where appropriate
- Cross-reference related documentation
- Follow existing file naming conventions (kebab-case)
