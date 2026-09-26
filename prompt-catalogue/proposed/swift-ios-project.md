---
title: Swift Ios Project
trigger: ''
---
- Before `xcodebuild test` on a Simulator, boot it and wait: `xcrun simctl shutdown all`, `simctl boot <udid>`, `simctl bootstatus <udid> -b`, then sleep a few seconds.
- "Simulator device failed to launch … Busy (Application failed preflight checks)" means a cold or half-booted simulator, not a code failure; boot-and-wait, then retry once before investigating.
- A run.
