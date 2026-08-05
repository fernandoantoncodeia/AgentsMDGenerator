# Design

## Catalogue root resolution

`catalogue.py` replaces the module-level `CURATED_DIR` / `PROPOSED_DIR` constants with a resolver:

```
set_catalogue_root(path)          # explicit override (set once by server/CLI startup)
resolve_catalogue_dir() -> Path   # returns the prompt-catalogue dir or raises
curated_dir() / proposed_dir()    # = resolve_catalogue_dir() / "curated" | "proposed"
```

Precedence: explicit override (`--catalogue-root`) > `AGENTSMD_CATALOGUE_ROOT` > `./prompt-catalogue` > bundled snapshot. A candidate is normalized: if it contains `curated/` use it directly; if it contains `prompt-catalogue/curated/` use `<candidate>/prompt-catalogue`.

The bundled snapshot ships at `agentsmd/_assets/prompt-catalogue/` (curated only). `catalogue_is_read_only()` returns True when the resolved dir is the bundled one; write operations (`addcontent`, `addcategory`, `curatecontent`, `curatecategory`) call `_require_writable()` and refuse with a clear message. Reads (`list_curated`, `read_body`, `self_discipline_scan`) work against any resolved dir.

## Server and CLI wiring

- `server.py main()`: add `--catalogue-root`; call `catalogue.set_catalogue_root(...)`; replace the hard CWD check with `catalogue.resolve_catalogue_dir()` guarded by try/except that prints the resolution-order error and exits non-zero.
- `cli.py`: add a group-level `--catalogue-root` option (Click `@click.group` with `ctx`); set the override before dispatch. Replace `_ensure_master_repo()` with resolution: read commands tolerate the bundled snapshot, write commands call the writable guard.

## Packaging (hatchling)

`pyproject.toml`:

```
[tool.hatch.build.targets.wheel]
packages = ["agentsmd"]

[tool.hatch.build.targets.wheel.force-include]
"prompt-catalogue/curated" = "agentsmd/_assets/prompt-catalogue/curated"
".factory/skills/update-agents/SKILL.md" = "agentsmd/_assets/workflow/skills/update-agents/SKILL.md"
".factory/commands/update-agents.md" = "agentsmd/_assets/workflow/commands/update-agents.md"

[project.scripts]
agentsmd-install = "agentsmd.install:main"
```

The snapshot is regenerated from the live catalogue on every build, so the master repo stays the source of truth.

## Installer (`agentsmd/install.py`)

`agentsmd-install [--tool factory|claude|both] [--server-command <cmd>]`:

- MCP registration: merge an `agentsmd` stdio entry into `~/.factory/mcp.json` and `~/.claude.json` under `mcpServers`. Default command is `agentsmd-server` (PATH); `--server-command` overrides (e.g. an absolute `bin/agentsmd-serve` for operators). JSON is read, the `agentsmd` key is set, and the file is rewritten with other keys preserved; missing files are created.
- Workflow assets: copy the bundled `update-agents` SKILL.md to `~/.factory/skills/update-agents/` and `~/.claude/skills/update-agents/`, and the command md to `~/.factory/commands/` and `~/.claude/commands/`.
- Idempotent: re-running overwrites only the `agentsmd` MCP entry and the `update-agents` asset files; unrelated servers/skills/commands are untouched.
- Reports every path written.

## Backward compatibility

Running from the master repo CWD keeps working: `./prompt-catalogue` is resolved before the bundled snapshot, and it is writable, so operator commands behave exactly as before.
