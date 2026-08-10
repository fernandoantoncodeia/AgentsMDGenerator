## MODIFIED Requirements

### Requirement: Conditional catalog sections are applied only by trigger

The workflow SHALL read category metadata, curated bodies, proposed names, and caps through the configured MCP server. It SHALL prefer the corresponding `catalogue://` resource. If the MCP client does not provide resource-read capability, it MAY use the equivalent read-only compatibility tool (`catalogue_list_categories`, `catalogue_get_curated`, `catalogue_list_proposed`, or `catalogue_get_config`). It MUST NOT read a local `prompt-catalogue/` directory or use curation tools as a read fallback. Each category's `trigger:` field SHALL be evaluated against a deterministic scan of the target repo; the workflow SHALL splice the category into the output only when its trigger fires. Conditions that match a trigger-equivalent but have no entry in the central catalogue SHALL trigger an auto-add to the master catalogue via `catalogue_addcategory` with the operator later curating via `agentsmd curatecategory` in the master repo.

#### Scenario: Tool-only client generates a new AGENTS.md

- **WHEN** the configured MCP server is reachable and the client exposes only tools
- **THEN** the workflow uses compatibility read tools to evaluate triggers and splice curated bodies, then generates the baseline output subject to the existing failure modes

#### Scenario: Python trigger fires
- **WHEN** the target repo contains Python sources (e.g. `pyproject.toml`, `requirements*.txt`, `setup.py`, `*.py`)
- **THEN** the output AGENTS.md includes the Python-project hints catalog section, reading its body via `catalogue://curated/python-project`

#### Scenario: Windows COM trigger fires
- **WHEN** the target repo contains Windows COM automation code (e.g. pywin32, comtypes, office automation imports)
- **THEN** the output AGENTS.md includes the Windows COM hints catalog section, reading its body via MCP

#### Scenario: OpenSpec trigger fires
- **WHEN** the target repo contains an `openspec/` directory
- **THEN** the output AGENTS.md includes the OpenSpec-driven-changes catalog section, reading its body via MCP

#### Scenario: Self-documentation trigger fires
- **WHEN** the target repo has a documentation or spec system (e.g. README-driven development, ADR directory, docs site config)
- **THEN** the output AGENTS.md includes the self-documentation hints catalog section, reading its body via MCP

#### Scenario: Python curated entry fires
- **WHEN** the target repo contains Python sources AND the MCP server reports `python-project` in `catalogue://categories`
- **THEN** the output AGENTS.md includes the python-project section, fetched from `catalogue://curated/python-project`

#### Scenario: Python trigger matches but no curated entry exists
- **WHEN** the target repo contains Python sources but the MCP server does not list `python-project` in `catalogue://categories`
- **AND** the MCP server does not list `python-project` in `catalogue://proposed-list` either
- **THEN** the workflow auto-emits `catalogue_addcategory(name="python-project", trigger="*.py files present", body="<starter>")` via MCP and reports `Auto-added to proposed catalogue: python-project (matched by: *.py files present)`. The workflow does not splice the proposed entry into AGENTS.md in the same invocation.

#### Scenario: OpenSpec curated entry fires
- **WHEN** the target repo contains an `openspec/` directory AND the MCP server lists `openspec-driven` in `catalogue://categories`
- **THEN** the output AGENTS.md includes the openspec-driven section, fetched via MCP

#### Scenario: Unrelated trigger does not fire
- **WHEN** the target repo contains Go sources and no Python, no OpenSpec, no Windows COM, and no docs system
- **THEN** the output AGENTS.md SHALL NOT include the python-project, openspec-driven, windows-com, or self-documentation sections

#### Scenario: Hard isolation against proposed folder for splice decisions
- **WHEN** the workflow decides what to splice into AGENTS.md
- **THEN** it reads ONLY curated category bodies through the MCP server; it does not list or read any proposed resource or any local `prompt-catalogue/` directory

#### Scenario: Auto-add to proposed is the only way to seed new categories
- **WHEN** the workflow detects a trigger that has no curated coverage
- **THEN** it MUST propose the entry through the MCP server; it MUST NOT write directly to any local or remote `curated/` directory and it MUST NOT splice the proposed entry into AGENTS.md in the same invocation

#### Scenario: Resource-capable client remains supported

- **WHEN** the client can read MCP resources
- **THEN** the workflow uses the resource URIs and does not require compatibility tools

#### Scenario: Read fallback is unavailable

- **WHEN** neither resource reads nor the matching compatibility tool can be used
- **THEN** the workflow reports the MCP read-path error and preserves the existing create/refresh write safety behavior
