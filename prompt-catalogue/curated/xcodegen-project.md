---
title: Xcodegen Project
trigger: project contains project.yml at the repo root (XcodeGen manifest)
---
- Run `xcodegen generate` after adding, deleting, renaming, or moving Swift files.
- Run `xcodegen generate` after editing `project.yml`.
- Never hand-edit `*.xcodeproj/project.pbxproj`; edit the manifest and regenerate.
- Regeneration keeps the Xcode project file list synchronized with the filesystem.
