---
title: Mermaid Diagrams
trigger: project contains Markdown or docs with ```mermaid fences, or *.mmd files
---
- In `flowchart`/`graph` diagrams, wrap any node or edge label containing curly braces in double quotes; an unquoted `{` opens a rhombus node and yields a parse error or empty render.
- Never mix edge-label styles on one edge: use `A -- text --> B` or `A -->|text| B`, never both on the same edge.
- Combine a condition and an action into a single quoted label rather than chaining two label forms.
- Sequence diagrams are exempt from the brace rule; braces only break `flowchart` and `graph`.
- Render or lint a diagram before committing it; a broken diagram fails silently on most Markdown hosts.
