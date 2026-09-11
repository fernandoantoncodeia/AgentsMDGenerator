---
title: Security Sensitive Surface Guardrail
trigger: default-on
---
- Maintain an explicit list of security-sensitive files and functional areas.
- Sensitive areas: auth/session gates, credential and secret storage, cryptography, data deletion, privacy consent, network trust boundaries.
- Any diff touching a listed file or area triggers an independent security review before the change ships.
- The reviewer must have no prior stake in the fix and must check the change against real threats, not the author's own reasoning.
- Record the review's verdict explicitly; never let an open finding ship silently or be waived by the implementer.
- Keep the list current; treat a missing entry as a gap to close, not an oversight to ignore.
