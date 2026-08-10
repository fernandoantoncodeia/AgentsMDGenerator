---
description: Generate or refresh AGENTS.md from the central prompt catalogue via MCP. First invocation creates the file, subsequent invocations refresh it.
argument-hint: "[path?]   (optional target repo path; defaults to the current working directory)"
---

The operational behaviour and guardrails live in the skill at `.claude/skills/update-agents/SKILL.md`. Read that skill before invoking the workflow.

`/update-agents` is now an MCP client. The consumer project no longer hosts a local `prompt-catalogue/`. The server launches locally over stdio. Configure it via one of:

- `.agentsmd/mcp.json` at the consumer root: `{ "serverUrl": "bin/agentsmd-serve", "transport": "stdio" }` (the value is the path to the launch script or `agentsmd-server` binary)
- Environment variable `AGENTSMD_MCP_URL`
- CLI argument: `/update-agents --mcp-url <url>`

Factory droids can also register the server in `.factory/mcp.json` (stdio, `command: bin/agentsmd-serve`) so the catalogue tools load automatically.

The skill reads only curated category metadata and bodies from the MCP server. Catalogue management (add, curate, browse) is performed by operators in the AgentsMDGenerator master repo using the `agentsmd` CLI.

If the client exposes MCP tools but not resource reads, the skill uses the server's read-only compatibility tools (`catalogue_list_categories`, `catalogue_get_curated`, `catalogue_list_proposed`, and `catalogue_get_config`).
