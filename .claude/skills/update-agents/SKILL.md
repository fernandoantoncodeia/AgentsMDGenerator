---
name: update-agents
description: Generate or refresh AGENTS.md from the central prompt catalogue via MCP. Operational workflow only; no consumer prompt bodies live here.
allowed-tools: Read, Write, Edit, Glob, Grep, LS, Bash, AskUser
license: MIT
compatibility: agents-md-generator >= 0.3
metadata:
  workflow: /update-agents
  source-of-truth: central MCP catalogue
---

# update-agents

**Hard isolation guardrail.** This workflow is an MCP client. It reads ONLY curated category metadata and bodies from the configured `agentsmd-mcp-server`. It MUST NOT read any local `prompt-catalogue/` directory. It does NOT call curation tools (`catalogue_curatecontent`, `catalogue_curatecategory`).

This file is operational. Consumer-facing prompt bodies live in the central catalogue, served by the MCP server in the AgentsMDGenerator master repo.

## 1. MCP configuration discovery

Resolve the MCP server endpoint in this order:

1. CLI argument `--mcp-url <url>` (used as `/update-agents --mcp-url <url>`).
2. Environment variable `AGENTSMD_MCP_URL`.
3. Consumer-root file `.agentsmd/mcp.json` with keys `serverUrl` and optional `transport` (`stdio` or `sse`).
4. If none are present, refuse to run with `error: no MCP server configured; create .agentsmd/mcp.json or set AGENTSMD_MCP_URL`.

If `transport` is omitted, infer from the URL: `http://` or `https://` → `sse`; otherwise `stdio`. For `stdio`, `serverUrl` is the absolute path to the `agentsmd-server` binary.

## 2. Mode detection

Determine whether to create or refresh:

- If `<agent-root>/AGENTS.md` does not exist → `Mode = create`.
- If it does exist → `Mode = refresh`.
- `<agent-root>` resolves to the optional path argument; default is the current working directory.

## 3. Connect to MCP server and read metadata

1. Connect to the MCP server using the resolved configuration.
2. Read `catalogue://categories`. The response is a list of `{name, title, trigger, heuristic}` objects. If the client does not expose MCP resource reads, call the equivalent read-only tool `catalogue_list_categories`.
3. If the connection fails, fail gracefully: in create mode write nothing; in refresh mode preserve the existing `AGENTS.md` and report the error.

Resource compatibility: use `catalogue://categories`, `catalogue://curated/<category>`, `catalogue://proposed-list`, and `catalogue://config` when resource reads are available. Otherwise use the matching read-only tools `catalogue_list_categories`, `catalogue_get_curated(category)`, `catalogue_list_proposed`, and `catalogue_get_config`. These tools are read-only fallbacks; never substitute local `prompt-catalogue/` reads or curation tools.

## 4. Trigger evaluation (deterministic, local)

For each category returned by `catalogue://categories`, evaluate its `trigger` against the consumer repo using cheap filesystem probes. Do not run language servers, package managers, or network calls. Triggers accepted:

- `default-on` → always fires.
- `project contains <comma-separated-basenames-or-globs>` → fires if any glob matches a real file under the consumer repo root.
- `project has <named-directory-or-file>` → fires if the path exists.
- compound: `AND` between two `project contains/has` clauses → fires only when both clauses match.
- heuristic triggers (`heuristic: true`) → surface in the completion summary rather than auto-splicing.

A trigger whose evaluation is inconclusive is treated as NOT firing. Surface it in the completion summary as `Inapplicable trigger: <title>`.

## 5. Read curated bodies for firing categories

For each category whose trigger fires, request `catalogue://curated/<category>` and read the body, or call `catalogue_get_curated(category)` when resource reads are unavailable. The body is spliced verbatim under `## <frontmatter.title>`. Do NOT read `catalogue://proposed/<category>` for splicing.

## 6. Required baseline sections

Always include, regardless of mode:

1. `<!-- coding_guidelines -->` open + `# <Project Name>` line taken from the consumer repo's `<root>/pyproject.toml` `[project].name` when present, else the directory basename.
2. `## Commands` — pointer into the consumer's own tooling (mention OpenSpec only when `openspec/` is present).
3. `## Be a colleague` — three paragraphs from the sourced catalogue entry `short-and-imperative.md`'s sibling content (splice from `short-and-imperative.md` and `tool-erratic.md`).
4. `## When the embedded guidance drifts` — short pointer that operators can run `/update-agents` again.

In refresh mode, do NOT add or remove mandatory sections except by editing them in-place to fix drift.

## 7. Splice pass

For each curated entry whose trigger returned True, splice the body verbatim under a `## <frontmatter.title>` heading. Insertion order:

1. After the `## Commands` section.
2. Then in alphabetical order by `title` for parity across refresh invocations.

## 8. Auto-add-to-proposed (D8)

When the trigger-scan finds a clear signal that a category SHOULD be present but does not yet have a curated entry (not listed in `catalogue://categories` and not in `catalogue://proposed-list`):

1. Derive a candidate category filename in `kebab-case`.
2. Compose a `--body` of three to five short imperative rules based on the detected signal.
3. Emit the MCP tool call `catalogue_addcategory(name=<derived>, trigger="<evidence-derived rule>", body="<starter>")`.
4. Reflect this in the completion summary as `Auto-added to proposed catalogue: <derived> (<one-line evidence>)`.
5. Do NOT splice the proposed entry into AGENTS.md. The curated set remains unchanged for this `/update-agents` invocation.

If the trigger-scan is too weak to derive a sensible starter body, do NOT auto-add. Report the gap as `Applicable-but-not-curated: <derived>`.

If a proposed entry already exists for the same derived category, report `Auto-add skipped (proposed duplicate): <derived>`.

## 9. Project-specific rules stay local

If a discovered rule applies only to this consumer project (e.g. a build error unique to this repo), do NOT call any MCP tool. Surface it as `Project-specific rule: <rule>` and let the user paste it into the project's `AGENTS.md` under a project-specific section.

## 10. Trim pass

The output AGENTS.md must respect the AGENTS.md line and byte caps read from `catalogue://config`, or `catalogue_get_config` when resource reads are unavailable (defaults: 512 lines, 32 KiB). Read them at the start of the trim pass.

- After every edit, re-read the file in full.
- Cut verbose prose; prefer imperatives and bullets.
- Drop near-duplicate rules across spliced sections.
- Re-run the trim pass until the file is under the configured AGENTS.md line cap (default 512) OR every remaining line is non-redundant and required.

The per-category cap (from `catalogue://config`, default 32 lines) is enforced at the catalogue layer, not here.

## 11. CLAUDE.md mirror

Write `<agent-root>/CLAUDE.md` if it does not already exist, with a single line:

```
@AGENTS.md
```

If `<agent-root>/CLAUDE.md` exists, leave it untouched unless its first non-comment line is not `@AGENTS.md`. In that case, warn the operator and STOP — do not overwrite an existing `CLAUDE.md` body.

If the path argument points outside the consumer repo root, report `mirror skipped` and skip the mirror step.

## 12. Catalog self-discipline check

After the splice pass, read the bodies of all curated categories via `catalogue://curated/<category>` (or `catalogue_get_curated(category)` when needed) and run the four-rule self-discipline check:

1. File ≤ the configured per-category cap (from `catalogue://config`, default 32 lines).
2. Every bullet ≤200 chars.
3. Within-category near-duplicates (≤30 char edit distance).
4. `trigger:` field present in metadata.

The scan is read-only. It MUST NOT refuse the `/update-agents` invocation. Per-file form in the completion summary:

- `ok` — passes all four.
- `<n> lines (cap <configured>)` — over the per-category cap.
- `bullet <i> exceeds 200 chars (<n> chars)` — over-length bullet.
- `near-duplicate vs bullet <j> (edit distance <n>)` — within-category dedupe candidate.
- `missing trigger:` — HARD finding, named as a contract violation.

The operator is expected to invoke `agentsmd curatecontent <cat>` in the master repo to repair flagged entries.

## 13. Completion summary

Output a single prose block listing:

- Mode (`create` or `refresh`).
- MCP server endpoint used (or the failure reason if unreachable).
- Sections spliced (alphabetical list of curated filenames).
- `Auto-added to proposed catalogue: <derived>` lines, if any.
- `Inapplicable trigger: <title>` lines, if any.
- `Applicable-but-not-curated: <derived>` lines, if any.
- `Project-specific rule: <rule>` lines, if any.
- Project anchor used.
- CLAUDE.md mirror outcome.
- `Catalog self-discipline check:` section listing one line per curated file.
- Final AGENTS.md line count.

Do NOT include any prompt body content in the summary.

## 14. Failure modes

- MCP server unreachable in create mode → write nothing and report `error: MCP server unreachable; no AGENTS.md created`.
- MCP server unreachable in refresh mode → preserve the existing `AGENTS.md` and report `error: MCP server unreachable; existing AGENTS.md preserved`.
- Trigger scan returns zero curated entries → emit `Inapplicable trigger: <title>` for every curated entry, splice only the baseline. The file remains valid AGENTS.md.
- Missing frontmatter in a category → log the category, skip it, surface in the completion summary. Do NOT abort.
- Heuristic trigger → surface in the completion summary rather than auto-splicing.
- Catalog self-discipline scan flags a curated file → surface in the completion summary; do NOT abort.
- Local `prompt-catalogue/` directory present in the consumer project → ignore it and report `Ignoring local prompt-catalogue/; use the MCP server instead`.
