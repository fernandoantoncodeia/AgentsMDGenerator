---
title: Ux Persona Panel Review
trigger: project contains a UI source directory (Views, Screens, Components, or platform
  UI folders such as SwiftUI/UIKit, Android layouts/Compose, React/Vue/Svelte components)
---
- Never let a single reviewer, human or agent, approve a UX/UI-affecting change alone before it ships.
- Run at least two independent lenses: platform-native interaction fidelity, and a dedicated brand/visual-identity reviewer who owns palette, iconography, and composition and blocks dilution.
- Keep each lens isolated — a separate pass or persona per lens — then consolidate the findings into one review record before merging.
- If a persona-panel or multi-persona swarm mechanism is already available in this project's tooling, use it; otherwise simulate the panel role-by-role.
