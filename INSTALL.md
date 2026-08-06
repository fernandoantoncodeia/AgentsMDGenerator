# Installing and using the AgentsMD generator

The generator is a local MCP server (stdio) plus a `/update-agents` workflow. Once installed, open any project and run `/update-agents` to create or refresh that project's `AGENTS.md` from the curated catalogue.

Distribution is an **editable install from a local checkout** (`pip install -e <path>`). There is no PyPI package; everyone clones this repo and installs it in place, so the MCP server always serves the **live** catalogue in your checkout.

## Install (any machine)

```bash
git clone https://github.com/fernandoantoncodeia/AgentsMDGenerator.git
cd AgentsMDGenerator
pip install -e .          # provides agentsmd, agentsmd-server, agentsmd-install
agentsmd-install --server-command "$(pwd)/bin/agentsmd-serve"
```

`agentsmd-install` writes a user-level MCP registration and installs the `update-agents` skill + command for both Factory (`~/.factory/`) and Claude (`~/.claude/`). It is idempotent and merges into existing config (it never clobbers unrelated servers, skills, or commands). Options:

- `--tool factory | claude | both` (default `both`)
- `--server-command <cmd>` (default `agentsmd-server` on PATH)

Point `--server-command` at the checkout's `bin/agentsmd-serve` (absolute path). That launcher enters the repo before starting, so the server serves `./prompt-catalogue` from your checkout regardless of which project you are working in.

Then, in any project:

```
/update-agents            # create AGENTS.md, or refresh/review an existing one
```

## Editing the catalogue (operator)

The catalogue lives only in this checkout at `prompt-catalogue/`. Edit it with the operator CLI from the repo root:

```bash
agentsmd list
agentsmd status
agentsmd addcontent <category> --body "<rule>"
agentsmd curatecontent <category>
```

Because the install is editable and the server serves the live checkout, catalogue edits are picked up on the next `/update-agents` run with no reinstall.

## Manual configuration (no installer)

User-level MCP registration for **Factory** (`~/.factory/mcp.json`) or **Claude** (`~/.claude.json`), under `mcpServers`. Use the absolute path to your checkout's launcher:

```json
{
  "mcpServers": {
    "agentsmd": {
      "type": "stdio",
      "command": "/absolute/path/to/AgentsMDGenerator/bin/agentsmd-serve",
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

`bin/agentsmd-serve` relies on step 3 by entering the checkout before launch. If none resolve, the server and CLI exit with an error naming this order.

## Line caps (configurable)

Two caps have configurable defaults:

- Per-category curated file: **32 lines** (`category_max_lines`)
- Generated AGENTS.md: **512 lines** (`agents_md_max_lines`) plus a **32 KiB** byte cap (`agents_md_max_bytes`)

Each value resolves per-key with precedence **environment variable > `caps.json` in the catalogue root > built-in default**:

| Cap | Env var | `caps.json` key | Default |
| --- | --- | --- | --- |
| Per-category lines | `AGENTSMD_CATEGORY_MAX_LINES` | `category_max_lines` | 32 |
| AGENTS.md lines | `AGENTSMD_AGENTS_MD_MAX_LINES` | `agents_md_max_lines` | 512 |
| AGENTS.md bytes | `AGENTSMD_AGENTS_MD_MAX_BYTES` | `agents_md_max_bytes` | 32768 |

Copy `prompt-catalogue/caps.json.example` to `prompt-catalogue/caps.json` and edit to override. A malformed `caps.json` or a non-positive value is rejected with an error. Inspect the resolved values with `agentsmd caps`; clients can read them from the `catalogue://config` MCP resource.
