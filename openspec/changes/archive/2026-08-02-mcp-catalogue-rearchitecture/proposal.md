# Change: mcp-catalogue-rearchitecture

## Why

The current architecture puts the catalogue (`prompt-catalogue/`) inside each consumer project alongside the generated `AGENTS.md`. The only guard against an LLM reading every prompt body is a sentence in the skill file: "read only `prompt-catalogue/curated/`". That is prompt-level isolation, not physical separation. If the LLM's context widens or a tool misreads the instruction, all catalogue prompts become visible to the project agent.

This change moves the catalogue out of the project context entirely. The catalogue becomes a service accessed via MCP (Model Context Protocol). The project only ever sees the specific category bodies it asks for, evaluated against its own trigger scan. The catalogue server is a simple file service with no LLM logic. Curation is performed by a deterministic operator CLI in the master repo. Best-practices discovery continues to use the existing six-source crawler, but as an operator-only skill that proposes CLI commands rather than writing directly to the catalogue.

## What Changes

- **BREAKING: Move the catalogue out of consumer projects.** `prompt-catalogue/` will only exist in the AgentsMDGenerator master repo. Consumer projects will no longer carry a local catalogue. They will connect to the master via MCP.
- **New MCP server** in the master repo. A Python package exposing MCP resources (`catalogue://categories`, `catalogue://curated/<cat>`, `catalogue://proposed/<cat>`) and tools (`catalogue_addcontent`, `catalogue_addcategory`, `catalogue_curatecontent`, `catalogue_curatecategory`, `catalogue_fetch_sources`). The server runs no LLM and does not scan projects.
- **New deterministic operator CLI** `agentsmd`. Commands: `addcontent`, `addcategory`, `curatecontent`, `curatecategory`, `list`, `status`. This CLI operates directly on the catalogue files in the master repo. No LLM logic.
- **Rewrite `/update-agents` skill.** The project skill becomes a client: it reads the catalogue metadata via MCP, scans the project locally, evaluates triggers locally (D2), reads only the firing category bodies via MCP, assembles `AGENTS.md`, and writes it along with `CLAUDE.md`. If the MCP server is unreachable, it fails gracefully and leaves the existing `AGENTS.md` unchanged.
- **Remove `/refresh-agents-content` project skill.** Catalogue management is no longer a project concern. The project can still propose generic rules via MCP tools called from the feedback loop, but curation is operator-only.
- **Rewrite `prompt-catalogue/curated/build-error-feedback-loop.md`.** The entry will now instruct: project-specific rules go directly to the project's `AGENTS.md`; generic rules are proposed to the catalogue via MCP (`catalogue_addcontent` / `catalogue_addcategory`).
- **Modify the best-practices discovery flow.** The existing `agents-md-refresh` capability (six-source crawler) becomes an operator-only skill. It fetches sources and diffs them, then outputs suggested `agentsmd addcontent` / `agentsmd addcategory` commands for the operator to run deterministically. It does not stage OpenSpec changes for catalogue updates; it only proposes.
- **Add Docker support.** A Dockerfile for x86_64 that runs the MCP server with SSE transport on a configurable port.
- **Remove the `no-capability-content-fix` stub spec.** The stub is no longer needed once the architecture change makes its purpose obsolete.
- **Deprecate the local-file catalogue workflow.** Any project still using a local `prompt-catalogue/` is unsupported and must connect to the MCP server.

## Capabilities

### New Capabilities

- `agentsmd-mcp-server`: The MCP server that exposes the catalogue as resources and tools. No LLM logic; no project scanning.
- `agentsmd-operator-cli`: The deterministic `agentsmd` command-line interface for catalogue management in the master repo.

### Modified Capabilities

- `agents-md-generation`: The `/update-agents` workflow changes from local catalogue reads to MCP client reads. Trigger evaluation moves to the project skill (D2). Offline behaviour is graceful failure.
- `prompt-catalogue-management`: The catalogue is no longer a local filesystem surface inside the project. Reads and writes go through MCP. Curation tools (`curatecontent`, `curatecategory`) are restricted to the operator CLI. Proposing tools (`addcontent`, `addcategory`) are available to both the project agent and the operator CLI.
- `agents-md-refresh`: The best-practices discovery workflow becomes operator-only. It no longer writes to the catalogue or stages OpenSpec changes for catalogue content. Instead, it outputs CLI commands for the operator to execute.

## Impact

- **New files in master repo:** Python package `agentsmd/`, `Dockerfile`, `docker-compose.yml` (optional), CLI entry points, and MCP server entry point.
- **New file in consumer projects:** `.agentsmd/mcp.json` or equivalent configuration pointing to the MCP server. The project can also use an env var or CLI argument for the same purpose.
- **Rewritten files:** `.claude/skills/update-agents/SKILL.md`, `prompt-catalogue/curated/build-error-feedback-loop.md`.
- **Deleted files:** `.claude/skills/refresh-agents-content/SKILL.md`, `.claude/commands/refresh-agents-content.md`, `.claude/commands/update-agents.md` (replaced with the MCP-aware version), and the `no-capability-content-fix` stub spec.
- **No longer shipped to consumer projects:** `prompt-catalogue/` directory.
- **Breaking change for existing consumers:** Projects that previously had a local catalogue must delete it and configure the MCP server URL. Their next `/update-agents` invocation will generate a fresh `AGENTS.md` from the central catalogue.
- **Operator workflow change:** Operators use `agentsmd addcontent`, `agentsmd addcategory`, `agentsmd curatecontent`, `agentsmd curatecategory` instead of slash commands. Best-practices discovery is still invoked via an operator skill, but it only proposes commands.
