---
title: Branch and worktree safety
trigger: default-on
---
- Never delete or recommend deleting a branch, worktree, stash or remote ref until its work is proven in the target: `git cherry -v` shows no `+` lines, or a full merge is done.
- Never delete a branch that holds tested or running code. A branch the running service was started from is live code: keep its checkout and ref until the target is deployed from and tested.
- A branch is not "superseded" because a sibling's subject or message sounds the same. Verify by content: run the branch-only tests against the target and diff behaviour.
- Never record a branch as merged with `git merge -s ours`, `-X ours` or any resolution that keeps one side's tree. Resolve the conflicts for real and review them.
- For "merge all and delete the rest": list each branch's unique commits (`git log <target>..<branch>`), merge each for real, run the full tests, then delete only branches reachable from the target.
- A destructive git step blocked by a permission check means verify, not rephrase. Stop, report what is unverified, and let the user decide.
