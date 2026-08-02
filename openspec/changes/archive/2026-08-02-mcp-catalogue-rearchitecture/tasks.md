# Tasks: MCP Catalogue Rearchitecture

## 1. Create the `agentsmd` Python package

- [x] Create `agentsmd/__init__.py`.
- [x] Create `agentsmd/catalogue.py` with functions to read and write `prompt-catalogue/curated/` and `prompt-catalogue/proposed/`, including pre-trim, dedupe, split, and length checks.
- [x] Create `agentsmd/trim.py` with the trim-pass logic (dedupe ≤30 char edit distance, trim verbose trailers, split bullets >200 chars).
- [x] Create `agentsmd/mcp_types.py` with the resource and tool definitions.
- [x] Create `agentsmd/server.py` implementing the MCP server with stdio and SSE transports.
- [x] Create `agentsmd/cli.py` implementing the `agentsmd` operator CLI.
- [x] Create `agentsmd/pyproject.toml` with package metadata and dependencies (`mcp`, `click`, `pyyaml`, `requests`).

## 2. Implement the MCP server

- [x] Expose `catalogue://categories` resource returning `{name, title, trigger}` metadata.
- [x] Expose `catalogue://curated/<category>` and `catalogue://proposed/<category>` resources.
- [x] Expose `catalogue://proposed-list` resource.
- [x] Implement `catalogue_addcontent(category, body)` tool writing to `proposed/` after pre-trim.
- [x] Implement `catalogue_addcategory(name, trigger, body)` tool writing to `proposed/` after pre-trim.
- [x] Implement `catalogue_curatecontent(category)` tool restricted to operators.
- [x] Implement `catalogue_curatecategory(name)` tool restricted to operators.
- [x] Implement `catalogue_fetch_sources(urls[])` tool returning raw bodies and timestamps.
- [x] Implement `--transport stdio` and `--transport sse` startup modes.
- [x] Add operator restriction: curation tools reject project-skill callers.

## 3. Implement the operator CLI

- [x] Implement `agentsmd addcontent <category> --body <text>`.
- [x] Implement `agentsmd addcategory <name> --trigger <rule> --body <text>`.
- [x] Implement `agentsmd curatecontent <category>` with `--force` support.
- [x] Implement `agentsmd curatecategory <name>` with `--force` support and remap candidates.
- [x] Implement `agentsmd list`.
- [x] Implement `agentsmd status` running the self-discipline scan.
- [x] Implement `agentsmd browsecontent` operator skill (six-source fetch, diff, emit commands).
- [x] Enforce master-repo-only execution (check `prompt-catalogue/` exists).

## 4. Add Docker support

- [x] Create `Dockerfile` for x86_64 that installs the `agentsmd` package and runs the server with `--transport sse`.
- [x] Create `docker-compose.yml` (optional) for local SSE testing.

## 5. Rewrite the project skill

- [x] Rewrite `.claude/skills/update-agents/SKILL.md` to be an MCP client.
- [x] Read MCP configuration from `.agentsmd/mcp.json`, `AGENTSMD_MCP_URL`, or `--mcp-url`.
- [x] Fetch `catalogue://categories` and evaluate triggers locally.
- [x] Fetch `catalogue://curated/<category>` only for firing categories.
- [x] Assemble and write AGENTS.md + CLAUDE.md.
- [x] Implement graceful offline failure (preserve existing AGENTS.md in update mode).
- [x] Add self-discipline scan over MCP-fetched bodies.
- [x] Remove all references to local `prompt-catalogue/` from the project skill.
- [x] Replace `.claude/commands/update-agents.md` with the MCP-aware version.

## 6. Remove the old project skill

- [x] Delete `.claude/skills/refresh-agents-content/SKILL.md`.
- [x] Delete `.claude/commands/refresh-agents-content.md`.
- [x] Delete `.factory` mirrors if present.

## 7. Update the build-error-feedback-loop catalogue entry

- [x] Rewrite `prompt-catalogue/curated/build-error-feedback-loop.md` to route generic rules through `catalogue_addcontent` / `catalogue_addcategory` (project skill) or `agentsmd addcontent` / `agentsmd addcategory` (operator).
- [x] Allow project-specific rules to be pasted directly into the project's own AGENTS.md.
- [x] Include an explicit Never list forbidding direct edits to AGENTS.md for generic rules, `curated/` in the master repo, and skill bodies.

## 8. Clean up the stub spec

- [x] Delete `openspec/specs/no-capability-content-fix/` and its contents.
- [x] The spec delta `specs/no-capability-content-fix/spec.md` in this change already declares the stub removed; during apply, delete the directory and let `openspec archive` sync the removal.

## 9. Validate and archive

- [x] Run `openspec validate mcp-catalogue-rearchitecture --strict`.
- [x] Run `openspec show mcp-catalogue-rearchitecture --json --deltas-only` and verify every requirement is listed.
- [x] Run smoke tests for the MCP server, CLI, and project skill.
- [x] Run `openspec archive mcp-catalogue-rearchitecture -y`.

## 10. Update AGENTS.md

- [x] Run `/update-agents` against the master repo (using the MCP server) to refresh `AGENTS.md` with the new workflow description.
