---
title: Agent Tool Discipline
trigger: default-on
---
- Don't fork for a couple of tool calls whose results you need immediately to continue the turn — forking is for output you don't want in context, not synchronous quick lookups.
- Reserve forking/subagents for long-running research, verbose tool noise, or independent parallel investigation whose raw output you don't need to keep.
- Never call the Agent tool with placeholder values (subagent_type/description/prompt: "n/a") as a no-op. The call still executes and fails visibly.
- If you don't intend to spawn an agent, don't call the Agent tool at all.
