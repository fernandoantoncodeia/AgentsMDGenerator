## Context

The Python MCP server already serves catalogue reads as resources. Some Factory/client integrations load only tools, so the workflow cannot issue `resources/read` despite a successful server connection.

## Decision

Add four read-only tools: `catalogue_list_categories`, `catalogue_get_curated`, `catalogue_list_proposed`, and `catalogue_get_config`. Their response payloads match the corresponding resource payloads. The curated-body tool accepts a category name and returns a not-found error payload without reading proposed content.

The workflow instructs the agent to attempt the resource URI first. If the client reports that resource reading is unavailable, it calls the matching compatibility tool. It must not substitute local catalogue reads or curation tools. The server retains both interfaces so resource-capable clients remain supported.

## Error handling

Read tools return the same structured error payloads used by resources. A catalogue resolution failure remains a server error. Missing curated categories are reported and skipped according to the existing workflow failure mode.

## Compatibility

Tool names are additive. Existing resources and write tools are unchanged. The implementation is deterministic and does not inspect consumer project files.
