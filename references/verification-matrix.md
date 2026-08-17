# Verification matrix

Choose the highest level required by any meaningful part of the change. Lower-level checks are included only when relevant; do not run redundant checks.

| Change type | Baseline | Notes |
|---|---:|---|
| README/docs/comments | V0 | No runtime verification unless docs are generated/validated |
| Formatting-only | V1 | Format only touched code |
| Runtime asset replacement | V1 | Check asset existence/readability; runtime/visual only if acceptance needs it |
| Localized UI/layout/copy | V2 | Static validation normally sufficient |
| Reusable component behavior | V2–V3 | V3 when behavior/state logic changed |
| State management | V3 | Prefer targeted existing tests |
| Business/domain logic | V3 | Prefer unit-level verification |
| API mapping/serialization/storage | V3 | Test smallest affected behavior |
| Navigation/routes | V3 | Runtime only if route integration cannot be validated otherwise |
| Pure Dart/JS dependency | V3 | Resolve deps + static + focused behavior |
| Native Flutter/RN dependency | V4 | Narrow platform build |
| Gradle/Podfile/Xcode/Manifest/Info.plist | V4 | Build only affected platform if known |
| Expo native app/config plugin change | V4 | Avoid prebuild/eject unless the repo's established workflow requires it |
| Code generation/native bindings | V4 | Run required generator, then narrow integration check |
| Permissions | V5 | Runtime behavior matters |
| Camera/mic/location | V5 | Runtime + platform permission flow |
| Deep links/universal/app links | V5 | Focused runtime launch/link check |
| Push notifications | V5 | Runtime/integration environment permitting |
| Background/lifecycle/platform channels | V5 | Runtime behavior matters |

## Risk modifiers

Raise the baseline when any of these apply:

- change crosses architectural boundaries;
- public/shared API behavior changes;
- migration or persisted data compatibility is involved;
- platform-specific behavior is introduced;
- task explicitly requires visual/runtime confirmation;
- repository rules or CI require stronger checks.

Do not raise the baseline merely because the task is large in lines changed. Raise it because the failure mode requires stronger evidence.

## Dependency caveat

`plan.py` treats dependency manifests/lockfiles as V3 by default because it does not attempt to infer package capabilities from the network. Raise to V4 when the dependency adds native code, autolinking, Pods/Gradle changes, a Flutter plugin, or an Expo config plugin.

## Working-tree caveat

Automatic Git detection sees all current working-tree changes. When unrelated user/agent changes already exist, pass this task's paths explicitly with `--files` so an unrelated high-risk file does not inflate verification.

## When a check fails

Use this sequence:

1. read the concise diagnostic;
2. inspect only the implicated code/log slice;
3. fix the evidenced cause;
4. rerun only checks invalidated by that fix;
5. escalate one level only if the current level cannot establish correctness.

Do not respond to an analyzer failure by immediately running a build. Do not respond to a build failure by clearing every cache.
