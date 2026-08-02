---
title: Self-Documentation
trigger: project has docs/, README.md driving API docs, ADR directory, OpenAPI/Swagger generator, docs-site config (Astro, Docusaurus, MkDocs), or an openspec/ directory
---

- Treat doc source of truth as code. Update README and ADRs in the same PR as the schema or API change.
- Run OpenAPI generation on every build; commit the generated spec even if you do not commit the rendered HTML.
- Pin external doc links to a snapshot date; flag broken links as separate issues rather than silently dropping them.
- Keep ADRs short and dated; one decision per file. Status: proposed, accepted, superseded, deprecated.
- For OpenSpec-driven repos, link ADRs to the matching `openspec/changes/` slug so reviewers can find both.
