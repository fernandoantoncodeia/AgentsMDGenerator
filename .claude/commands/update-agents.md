---
description: Generate or refresh AGENTS.md from the central prompt catalogue via MCP. First invocation creates the file, subsequent invocations refresh it.
argument-hint: "[path?]   (optional target repo path; defaults to the current working directory)"
---

The operational behaviour and guardrails live in the skill at `.claude/skills/update-agents/SKILL.md`. Read that skill before invoking the workflow.

`/update-agents` is now an MCP client. The consumer project no longer hosts a local `prompt-catalogue/`. Configure the MCP server via one of:

- `.agentsmd/mcp.json` at the consumer root: `{ "serverUrl": "http://localhost:3000/sse", "transport": "sse" }`
- Environment variable `AGENTSMD_MCP_URL`
- CLI argument: `/update-agents --mcp-url <url>`

The skill reads only curated category metadata and bodies from the MCP server. Catalogue management (add, curate, browse) is performed by operators in the AgentsMDGenerator master repo using the `agentsmd` CLI.
