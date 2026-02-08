# Explanation

Welcome to the explanation section! This section contains background information and conceptual guides to help you understand how mytt-scraper works and why it works that way.

## What You'll Find Here

Explanations in this section are:
- **Understanding-oriented** — focused on concepts and theory
- **Discursive** — takes a broader view, connects ideas
- **Background knowledge** — provides context for decisions and design
- **Not tutorial or reference** — these complement, not replace, other sections

## Available Explanations

### Architecture and Design

- **[System Architecture](architecture.md)** — Playwright login → cookies → requests → extraction pipeline
- **[How the Scraper Works](how-scraper-works.md)** — Overview of the scraping architecture
- **[Authentication Flow](authentication-flow.md)** — How login and session management work
- **[Why Playwright?](why-playwright.md)** — Rationale for using browser automation

### Data Understanding

- **[In-Memory vs Disk Tables](in-memory-vs-disk-tables.md)** — Why in-memory first; CSV fallback; Polars/DuckDB
- **[Understanding TTR Ratings](understanding-ttr.md)** — How the TTR system works
- **[Table Relationships](table-relationships.md)** — How extracted tables relate to each other
- **[Rate Limiting and Ethics](rate-limiting-ethics.md)** — Responsible data collection

### Technical Decisions

- **[CSV vs In-Memory Extraction](csv-vs-memory.md)** — Choosing the right approach for your use case
- **[API vs Playwright Search](api-vs-playwright.md)** — Trade-offs between search methods

---

> 📚 **Looking for something else?**
> - Learning the basics? See [Tutorials](../tutorials/index.md)
> - Need to solve a problem? See [How-To Guides](../how-to/index.md)
> - Need technical details? See [Reference](../reference/index.md)
