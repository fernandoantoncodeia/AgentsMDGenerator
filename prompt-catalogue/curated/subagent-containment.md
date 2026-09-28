---
title: Subagent Containment
trigger: default-on
---
- A prompt-only restriction on a subagent ("review-only, don't edit/write/spawn agents") is advisory, not enforced.
- A subagent inherits whatever tools its type grants regardless of prompt wording — `fork` inherits the caller's full toolset, including Edit/Write/Bash/Agent.
- Over a long or autonomous run with no human in the loop, a subagent may use tools it was told not to use.
- Never delegate a consequential, hard-to-reverse action to any subagent: archiving/finalizing a change, controlling a live service, `git push`, or writes outside its own project.
- Perform consequential actions yourself, gated on an explicit human go-ahead in that same turn — never on a subagent's own judgment that conditions were met.
- For a read-only/annotation-only task, use a tool-restricted agent definition, not `fork` or a full-access fresh agent — the boundary must come from tool access, not wording.
- Never trust a subagent's own "done"/"passed" summary for anything consequential — re-read the actual diff and rerun the actual tests yourself before acting on the claim.
