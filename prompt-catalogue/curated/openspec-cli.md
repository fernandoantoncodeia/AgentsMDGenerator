---
title: OpenSpec CLI Conventions
trigger: openspec/ directory exists at the repo root AND the consumer project runs openspec commands
---

- Run the OpenSpec lifecycle end-to-end, unattended. Every `openspec` / `npx openspec ...` invocation runs without interaction; chain propose → apply → archive without pausing.
- Always finish with `openspec archive <change> -y`.
- Validate with `npx openspec validate <change> --strict`.
- Inspect with `openspec show <change> --json --deltas-only`.
- List with `openspec list`.
- Status with `openspec status --change <name> --json`.
- Never invent CLI flags; confirm with `openspec <sub> --help` first.
- Treat missing change context as a prompt to use `AskUser` rather than guessing a slug.
