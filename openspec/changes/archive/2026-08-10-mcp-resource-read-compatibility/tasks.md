## 1. MCP server compatibility reads

- [x] 1.1 Add constants for the four read-only compatibility tools.
- [x] 1.2 Implement the four tools with resource-equivalent payloads and error handling.
- [x] 1.3 Add focused tests for tool registration, payloads, and read-only behavior.

## 2. Workflow fallback

- [x] 2.1 Update `.claude/skills/update-agents/SKILL.md` to define resource-first, tool-fallback reads.
- [x] 2.2 Mirror the workflow update to `.factory/skills/update-agents/SKILL.md`.
- [x] 2.3 Update both command wrappers to document the tool-only client compatibility path.

## 3. Verification

- [x] 3.1 Validate the OpenSpec change strictly.
- [x] 3.2 Run focused tests and verify both workflow copies are identical.
