---
title: Swift Ios Project
trigger: project contains an *.xcodeproj or *.xcworkspace directory, a Package.swift,
  or *.swift sources
---
- Build and test from the command line with `xcodebuild -scheme <scheme> -destination '<destination>'`; do not assume the Xcode GUI is available.
- Never hand-edit `*.xcodeproj/project.pbxproj`; change targets through Xcode or a project generator.
- Store credentials and tokens in the Keychain, never in `UserDefaults` or a plist.
- Prefer `async`/`await` with `URLSession` over completion handlers in new code.
- Regenerate API model types from the contract instead of hand-writing `Codable` structs that mirror an existing spec.
