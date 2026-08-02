# Design: MCP Catalogue Rearchitecture

## Components

1. **agentsmd-mcp-server** — Python MCP server running in the AgentsMDGenerator master repo. It exposes the catalogue as MCP resources and tools. No LLM. No project scanning. Supports `stdio` and `SSE` transports.
2. **agentsmd-operator-cli** — Deterministic `agentsmd` command in the master repo for curation and direct catalogue edits.
3. **update-agents project skill** — MCP client that runs in a consumer project, evaluates triggers locally, and assembles AGENTS.md.
4. **agentsmd browsecontent operator skill** — Operator-only six-source crawler that emits `agentsmd` commands and OpenSpec changes for Sourced Principles.

## Repository Layout

### AgentsMDGenerator master repo

```
agentsmd/
  __init__.py
  server.py           # MCP server entry point
  cli.py              # agentsmd CLI entry point
  catalogue.py        # read/write/catalogue operations
  trim.py             # pre-trim, dedupe, split logic
  mcp_types.py        # resource/tool definitions
  pyproject.toml      # package metadata + deps
Dockerfile            # x86_64 SSE server image
prompt-catalogue/
  curated/
  proposed/
.claude/skills/update-agents/SKILL.md          # MCP-aware project skill
.claude/commands/update-agents.md              # replaced
```

### Consumer project

```
AGENTS.md
CLAUDE.md
.agentsmd/mcp.json   # optional MCP configuration
```

No `prompt-catalogue/` directory in the consumer project.

## Data Flow

### /update-agents in a consumer project

1. Read `.agentsmd/mcp.json`, `AGENTSMD_MCP_URL`, or `--mcp-url`.
2. Connect to the MCP server.
3. Request `catalogue://categories`.
4. Scan the project locally for trigger evidence.
5. For each category whose trigger fires, request `catalogue://curated/<category>`.
6. Assemble AGENTS.md: mandated baseline + fired category bodies.
7. Write AGENTS.md and CLAUDE.md.
8. Run self-discipline scan over the fetched bodies and report.
9. If MCP is unreachable, fail gracefully and preserve the existing AGENTS.md.

### Project proposes a generic rule

1. Project skill calls `catalogue_addcontent(category, body)` or `catalogue_addcategory(name, trigger, body)` via MCP.
2. Server writes to `prompt-catalogue/proposed/<category>.md` in the master repo after pre-trim.
3. Operator later runs `agentsmd curatecontent <category>` or `agentsmd curatecategory <name>` in the master repo.

### Operator curates content

1. Operator runs `agentsmd curatecontent <category>` in the master repo.
2. CLI merges proposed into curated, applies dedupe, length checks, and trigger validation.
3. On success, the proposed file is removed.

### Best-practices discovery

1. Operator runs `agentsmd browsecontent` in the master repo.
2. The skill fetches the six canonical sources (via MCP or directly).
3. The skill diffs against `prompt-catalogue/curated/` and the Sourced Principles in the update-agents skill.
4. The skill emits `agentsmd addcontent` / `agentsmd addcategory` commands for catalogue changes.
5. For Sourced Principles changes, the skill stages an OpenSpec change under `openspec/changes/refresh-agents-md-content-<date>/`.

## Transport

- **stdio**: default. Used by Claude Desktop / Claude Code local configuration. The consumer project points to the server binary via `mcpServers` config.
- **SSE**: used by Docker or shared local services. Configurable port via `--port`.

## Configuration

Consumer projects use one of:

- `.agentsmd/mcp.json`:
  ```json
  {
    "serverUrl": "http://localhost:3000/sse",
    "transport": "sse"
  }
  ```
- Environment variable `AGENTSMD_MCP_URL` (and optional `AGENTSMD_MCP_TRANSPORT`).
- CLI argument `--mcp-url <url>` (used by `/update-agents --mcp-url ...`).

## Removed / Deprecated

- `.claude/skills/refresh-agents-content/SKILL.md` and `.claude/commands/refresh-agents-content.md` are deleted.
- `prompt-catalogue/` in consumer projects is unsupported.
- The `no-capability-content-fix` stub spec is removed from `openspec/specs/`.

## Error Handling

- Missing MCP configuration: refuse before any write.
- MCP unreachable in create mode: no AGENTS.md created.
- MCP unreachable in update mode: existing AGENTS.md preserved.
- Project skill blocked from curation tools: server returns 403-style error.
- Self-discipline scan findings are reported but non-blocking.
