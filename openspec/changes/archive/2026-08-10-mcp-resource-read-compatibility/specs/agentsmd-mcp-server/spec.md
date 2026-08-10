## ADDED Requirements

### Requirement: Server exposes read-only tool compatibility for catalogue resources

The server SHALL expose read-only tools `catalogue_list_categories`, `catalogue_get_curated`, `catalogue_list_proposed`, and `catalogue_get_config` for MCP clients that cannot read resources. Their successful payloads SHALL be equivalent to `catalogue://categories`, `catalogue://curated/<category>`, `catalogue://proposed-list`, and `catalogue://config` respectively.

#### Scenario: Tool-only client lists categories

- **WHEN** a client calls `catalogue_list_categories`
- **THEN** the server returns every curated category's `name`, `title`, `trigger`, and `heuristic` metadata without category bodies

#### Scenario: Tool-only client reads a curated body

- **WHEN** a client calls `catalogue_get_curated` with `category=python-project`
- **THEN** the server returns the curated body without YAML frontmatter

#### Scenario: Tool-only client reads caps and proposed names

- **WHEN** a client calls `catalogue_get_config` or `catalogue_list_proposed`
- **THEN** the server returns the resolved caps or proposed category names without modifying the catalogue

#### Scenario: Compatibility tools are read-only

- **WHEN** a client calls any compatibility read tool
- **THEN** the server performs no catalogue write and does not inspect consumer project files
