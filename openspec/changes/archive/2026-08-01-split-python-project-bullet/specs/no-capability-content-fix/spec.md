# no-capability-content-fix delta spec

This change is a content-only compliance fix. No capability requirements change.

## ADDED Requirements

### Requirement: This change introduces no spec-level requirement changes
The change `split-python-project-bullet` SHALL NOT introduce any new requirement, modify any existing requirement, rename any requirement, or remove any requirement. The compliance fix is brought into line with the per-bullet ≤200 char rule that already exists in the `prompt-catalogue-management` capability (added by `catalogue-write-discipline`).

#### Scenario: Validate passes
- **WHEN** `openspec validate split-python-project-bullet --strict` runs
- **THEN** the change is reported valid with zero delta against the synced specs

#### Scenario: Archive sync shows zero net change
- **WHEN** `openspec archive split-python-project-bullet -y` runs
- **THEN** the synced specs are unchanged or differ in zero net deltas (additions, modifications, removals all zero). The archive succeeds because `## MODIFIED Requirements` and `## ADDED Requirements` in any capability spec file are empty.
