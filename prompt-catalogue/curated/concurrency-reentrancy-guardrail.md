---
title: Concurrency Reentrancy Guardrail
trigger: project source contains async/await, actor, coroutine, or explicit lock/mutex/semaphore
  usage
---
- Maintain an explicit, curated list of files sensitive to reentrancy.
- Hazard shape: code that can re-enter a shared serial context (actor, lock, DB session, main queue) mid-transition and hang the app.
- Any diff touching a listed file requires an independent review focused specifically on reentrancy, deadlock, and hang risk — not just an ordinary code review.
- Keep the list current: add a file the moment a new hazard shape is found in production or testing; do not let it go stale.
- Run that review before considering the change done, even when it is not itself a bug fix.
