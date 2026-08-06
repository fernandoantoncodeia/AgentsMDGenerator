## REMOVED Requirements

### Requirement: Catalogue lives only in the AgentsMDGenerator master repo
**Reason**: Replaced by a requirement without the read-only snapshot allowance (see ADDED below). The "distributed package may ship a read-only snapshot" scenario is obsolete.
**Migration**: The single canonical writable catalogue is the checkout's `prompt-catalogue/`; the server serves it live via `bin/agentsmd-serve`.

## ADDED Requirements

### Requirement: Canonical catalogue lives only in the master repo checkout
The single canonical, writable copy of the catalogue SHALL be the `prompt-catalogue/` directory in the AgentsMDGenerator master repo checkout. Consumer projects SHALL NOT host a `prompt-catalogue/` directory in their source tree.

#### Scenario: Master repo contains the catalogue
- **WHEN** the operator inspects the AgentsMDGenerator master repo
- **THEN** `prompt-catalogue/curated/` and `prompt-catalogue/proposed/` exist and are the only canonical writable catalogue locations

#### Scenario: Consumer project does not contain the catalogue
- **WHEN** the operator inspects a consumer project after running `/update-agents`
- **THEN** there is no `prompt-catalogue/` directory in the project source, and the generated AGENTS.md does not depend on one
