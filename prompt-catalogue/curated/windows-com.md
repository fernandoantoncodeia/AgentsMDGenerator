---
title: Windows COM
trigger: project imports or bundles Windows COM automation (pywin32, comtypes, win32com.client, winrt, pythonnet, or any *.tlb / *.ocx reference)
---

- Match Python bitness to Office bitness: 64-bit Office requires 64-bit Python.
- Run automation scripts with elevation only when the caller genuinely needs admin; do not blanket-elevate.
- Stay out-of-process for long-running operations to avoid blocking the UI thread.
- Pair every `pythoncom.CoInitialize` with a `pythoncom.CoUninitialize` (use try/finally).
- Prefer late-bound dispatch (`win32com.client.Dispatch`) for prototypes; switch to early-bound after the API surface stabilizes.
- Generate wrappers via `comtypes.client.CreateObject` plus `GetModule` for typed `*.tlb` access.
