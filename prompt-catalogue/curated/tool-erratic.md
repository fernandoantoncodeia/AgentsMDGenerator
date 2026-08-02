---
title: Tool Erratic Behaviour
trigger: default-on
---

A tool-call mechanics failure (malformed JSON, rejected params, schema validation error) is NOT a decision point.

- Retry immediately with a simpler, safer form (one large edit → several single edits) without asking the user.
- Only stop and ask after two materially different approaches have both failed.
- Do not attribute the failure to user intent. Treat the API contract as the source of truth and reshape the call.
- If a tool repeatedly rejects the same conceptual operation, change the abstraction (write a small script, switch tools), not the input.
