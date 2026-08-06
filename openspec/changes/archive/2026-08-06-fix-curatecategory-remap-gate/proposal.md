## Why

`agentsmd curatecategory <name>` is unusable whenever two or more entries sit in `proposed/`. The command flags **every** other proposed entry as a "remap candidate" (there is no trigger-overlap check despite the comment claiming one) and then exits without promoting, with no flag to confirm or bypass. `--force` only overrides size caps. So an operator with unrelated drafts (e.g. `swift-ios-project`, `aws-cdk-typescript`, `java-quarkus-project`, `mermaid-diagrams`) can never promote any of them via `curatecategory`.

## What Changes

- Detect remap candidates by **genuine trigger-evidence overlap**: another proposed entry is a candidate only when its `trigger:` shares a distinctive token with `<name>`'s trigger (common words like "project", "contains", "file", "source" are ignored). Unrelated drafts no longer block promotion.
- Add a `--no-remap` flag so that, when genuine candidates exist, the operator can promote `<name>` as-is and leave the other drafts untouched. This preserves the "confirm remaps explicitly" intent while providing a path forward.
- When no genuine candidate exists, promote without prompting.

## Capabilities

### Modified Capabilities
- `agentsmd-operator-cli`: refine the `curatecategory` remap behavior (real overlap detection + `--no-remap`).

## Impact

- Code: `agentsmd/cli.py` (curatecategory command).
- Fixes a hard block that prevented curation whenever multiple unrelated proposals existed.
- Backward compatible: single-proposal promotion and genuine-overlap surfacing still work; the only new surface is the `--no-remap` flag.
