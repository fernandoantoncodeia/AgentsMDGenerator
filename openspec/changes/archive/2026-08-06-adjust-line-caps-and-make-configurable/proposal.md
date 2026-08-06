## Why

Two line caps are hardcoded: the per-category curated file cap (100) lives in `agentsmd/catalogue.py`, and the total AGENTS.md cap ("150-line soft cap + 32 KiB hard cap") lives only in the `update-agents` skills and a Sourced Principle. The operator wants different defaults (per-entry 32; AGENTS.md 512 lines, keeping the 32 KiB byte cap) and wants both caps overridable without editing code, via a JSON file in the catalogue root and via environment variables.

## What Changes

- New defaults: per-category curated cap **32 lines** (was 100); AGENTS.md **512 lines** (was 150 soft cap), 32 KiB byte cap retained.
- New config layer (`agentsmd/config.py`). Each cap resolves per-key with precedence **environment variable > `<catalogue-root>/caps.json` > built-in default**:
  - per-category: `AGENTSMD_CATEGORY_MAX_LINES` / `category_max_lines` (default 32)
  - AGENTS.md lines: `AGENTSMD_AGENTS_MD_MAX_LINES` / `agents_md_max_lines` (default 512)
  - AGENTS.md bytes: `AGENTSMD_AGENTS_MD_MAX_BYTES` / `agents_md_max_bytes` (default 32768)
- The per-category cap now flows through the resolver in every `catalogue.py` check (curatecontent/curatecategory/recurate refusals, `status` scan, `_suggest_fix`).
- The resolved caps are exposed read-only via the MCP resource `catalogue://config` and the new `agentsmd caps` CLI command, so the `update-agents` workflow reads the AGENTS.md cap instead of hardcoding it.
- Both `update-agents/SKILL.md` copies read the AGENTS.md cap from `catalogue://config`; the curated `short-and-imperative.md` bullet is updated from 150 to 512 (approved one-off).

## Capabilities

### Modified Capabilities
- `prompt-catalogue-management`: per-category cap default 32 and configurable; add the configurable-caps + `catalogue://config` requirement.
- `agentsmd-operator-cli`: `status` reflects the configured cap; add `agentsmd caps` command.
- `agents-md-generation`: AGENTS.md length discipline default 512 (32 KiB retained), read from `catalogue://config`; scan finding text reflects the configured cap.

## Impact

- Code: `agentsmd/config.py` (new), `agentsmd/catalogue.py`, `agentsmd/cli.py`, `agentsmd/server.py`, `agentsmd/mcp_types.py`.
- Assets: `.factory/skills/update-agents/SKILL.md`, `.claude/skills/update-agents/SKILL.md`, `prompt-catalogue/curated/short-and-imperative.md`, `prompt-catalogue/caps.json.example`, INSTALL.md.
- The new configurable-caps requirement's defaults supersede the literal "100-line" and "150-line" figures still quoted in older `curatecontent`/`curatecategory`/`browsecontent` requirements; the code emits the resolved number everywhere.
- Backward compatible: no caps.json and no env vars means the new defaults apply.
