---
title: Vite Web Frontend
trigger: project contains a vite.config.{js,ts,mjs} or a package.json depending on
  vite
---
- Build with `npx vite build` and check the reported `dist/` bundle size after every dependency addition; treat the project's stated size budget as a hard gate.
- Commit the lockfile and pin the Vite major in `package.json`; never install with `--no-save`.
- Never commit `dist/` or `node_modules/`; both are build output.
- Import modules explicitly; do not pass state between entry points through globals on `window`.
- Keep one `vite.config` per deployable frontend; do not let two config files describe the same site.
