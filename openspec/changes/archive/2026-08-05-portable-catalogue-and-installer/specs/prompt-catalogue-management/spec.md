## MODIFIED Requirements

### Requirement: Catalogue lives only in the AgentsMDGenerator master repo
The single canonical, writable copy of the catalogue SHALL be the `prompt-catalogue/` directory in the AgentsMDGenerator master repo. The distributed package MAY ship a read-only snapshot of `curated/` for offline reads; this snapshot lives inside the installed package, SHALL never be written to, and is not a copy inside consumer project source. Consumer projects SHALL NOT host a `prompt-catalogue/` directory in their source tree.

#### Scenario: Master repo contains the catalogue
- **WHEN** the operator inspects the AgentsMDGenerator master repo
- **THEN** `prompt-catalogue/curated/` and `prompt-catalogue/proposed/` exist and are the only canonical writable catalogue locations

#### Scenario: Consumer project does not contain the catalogue
- **WHEN** the operator inspects a consumer project after running `/update-agents`
- **THEN** there is no `prompt-catalogue/` directory in the project source, and the generated AGENTS.md does not depend on one

#### Scenario: Distributed package may ship a read-only snapshot
- **WHEN** the package is installed via pip or pipx
- **THEN** it MAY contain a read-only `curated/` snapshot used only to serve reads when no writable root is configured, and write operations against it are refused
