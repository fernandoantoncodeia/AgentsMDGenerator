# Installing and using the AgentsMD generator

The generator is a local MCP server (stdio) plus a `/update-agents` workflow. Once installed, open any project and run `/update-agents` to create or refresh that project's `AGENTS.md` from the curated catalogue.

There are two roles:

- **Consumer** - you want `/update-agents` in your projects. You do not edit the catalogue.
- **Operator** - you maintain the catalogue in this master repo and want the live catalogue served.

## Consumer quick start (any machine)

```bash
pipx install agentsmd          # or: pip install --user agentsmd
agentsmd-install               # wires Factory (~/.factory) and Claude (~/.claude)
```

`agentsmd-install` writes a user-level MCP registration and installs the `update-agents` skill + command for both tools. It is idempotent and merges into existing config (it never clobbers unrelated servers, skills, or commands). Options:

- `--tool factory | claude | both` (default `both`)
- `--server-command <cmd>` (default `agentsmd-server` on PATH)

Then, in any project:

```
/update-agents          # create AGENTS.md, or refresh/review an existing one
```

Consumers read a **read-only snapshot** of the curated catalogue bundled in the package, so no repo checkout is needed.

## Operator setup (this master repo)

Operators serve the **live** catalogue from a checkout so edits are reflected immediately:

```bash
git clone <this repo> AgentsMDGenerator && cd AgentsMDGenerator
pip install -e .        # provides agentsmd, agentsmd-server, agentsmd-install
agentsmd-install --server-command "$(pwd)/bin/agentsmd-serve"
```

`bin/agentsmd-serve` launches the server from the repo root, so it always serves `./prompt-catalogue`. Edit the catalogue with the operator CLI:

```bash
agentsmd list
agentsmd status
agentsmd addcontent <category> --body "<rule>"
agentsmd curatecontent <category>
```

## Manual configuration (no installer)

User-level MCP registration for **Factory** (`~/.factory/mcp.json`) or **Claude** (`~/.claude.json`), under `mcpServers`:

```json
{
  "mcpServers": {
    "agentsmd": {
      "type": "stdio",
      "command": "agentsmd-server",
      "connectTimeout": 30000
    }
  }
}
```

Then place the workflow files at the user level for each tool:

- Factory: `~/.factory/skills/update-agents/SKILL.md` and `~/.factory/commands/update-agents.md`
- Claude: `~/.claude/skills/update-agents/SKILL.md` and `~/.claude/commands/update-agents.md`

## Catalogue root resolution

The server and CLI resolve the catalogue directory in this order:

1. `--catalogue-root <path>` (a `prompt-catalogue` dir or a directory containing it)
2. `AGENTSMD_CATALOGUE_ROOT` environment variable
3. `prompt-catalogue/` in the current working directory
4. the read-only snapshot bundled in the installed package

Writes (`addcontent`, `addcategory`, `curatecontent`, `curatecategory`) require a writable root; they refuse to run against the bundled snapshot.
