## Why

Some MCP clients discover tools but do not expose resource-read operations to workflows. `/update-agents` then cannot read the catalogue even when its configured stdio server is healthy, blocking every new consumer project.

## What Changes

- Add read-only MCP tools that mirror the catalogue resources required by `/update-agents`.
- Make the workflow use resource reads when available and the read-only tool fallback otherwise.
- Keep resource endpoints, curated-only splicing, and operator write restrictions unchanged.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `agentsmd-mcp-server`: expose tool-based compatibility reads for catalogue data.
- `agents-md-generation`: permit the equivalent read-only MCP tools when resource reads are unavailable.

## Impact

Affected files are `agentsmd/server.py`, MCP constants, both `.claude/` and `.factory/` update-agents workflow copies, and MCP server / generation specs. No new dependencies or consumer-repository writes are introduced.
