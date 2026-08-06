## REMOVED Requirements

### Requirement: Package bundles a read-only curated snapshot
**Reason**: The distribution moves to editable local installs (`pip install -e <checkout>`). A checkout is always present and the server serves the live `prompt-catalogue/` via `bin/agentsmd-serve`, so the bundled snapshot is never consulted, is inert under editable installs, and risks drifting from the live catalogue.
**Migration**: Serve the live catalogue from the checkout via `bin/agentsmd-serve`, `--catalogue-root`, or `AGENTSMD_CATALOGUE_ROOT`. No consumer action is required.
