---
title: Android Emulator Testing
trigger: project contains an Android module (build.gradle(.kts) with com.android.application,
  or an AndroidManifest.xml)
---
- Before instrumented tests, boot the emulator and wait until it is ready: `adb wait-for-device`, then poll `adb shell getprop sys.boot_completed` until it returns `1`.
- Also wait for the package manager (`adb shell pm path android`) before installing or launching; a half-booted emulator fails installs and launches with misleading errors.
- A run.
- Run JVM unit tests (`./gradlew testDebugUnitTest`) without an emulator when they do not need one.
- Never keep an Android emulator and an iOS Simulator running together on a memory-constrained machine.
