# Changelog

## 0.2.0 — 2026-08-17

Public-preview hardening:

- include deleted files in change classification;
- distinguish runtime assets from documentation instead of treating images as V0 docs;
- stop inferring React Native from generic TypeScript/JavaScript alone;
- detect Flutter/RN manifests in nested app directories for monorepos;
- add task-local `--files` guidance for dirty/multi-agent working trees;
- make regex guards check changed lines by default, with optional whole-file scope;
- delete successful quiet-run logs by default and add optional timeout support;
- add Agent Skills metadata, OpenAI UI metadata, MIT license, helper tests, and behavior eval scenarios.
- add public release docs, examples, contribution/security guidance, GitHub templates, and CI.
- fix nested Flutter/RN manifest detection when the caller passes a relative root path.

## 0.1.0

Initial V0–V5 verification ladder, context budget, Flutter/RN adapters, rule routing, and quiet command runner.
