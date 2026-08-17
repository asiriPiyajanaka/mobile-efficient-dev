# Flutter adapter

Use this reference only for Flutter apps.

## Tool selection

Respect repository wrappers first:

1. If project guidance mandates FVM, use `fvm flutter` / `fvm dart`.
2. Otherwise, if the project clearly uses FVM (`.fvm/` or `.fvmrc`) and FVM is available, prefer FVM.
3. Otherwise use `flutter` / `dart`.

Do not install/change Flutter versions merely to perform routine verification unless the task requires it.

## Verification examples

### V1

For Dart edits, format only changed Dart files when practical:

```bash
dart format <changed-dart-files>
```

Avoid formatting the entire repository for a localized change unless repo policy requires it. For asset-only changes, do not run Dart formatting just to satisfy V1; check the changed asset/path instead.

### V2

Run static validation once after the coherent edit batch:

```bash
flutter analyze
```

Use `run_quiet.py` if analyzer output is likely to be noisy.

### V3

Prefer the smallest existing relevant test:

```bash
flutter test test/path/to/relevant_test.dart
```

If no relevant test exists, do not automatically run the entire test suite just to satisfy the level. Choose the cheapest meaningful behavior check and report the limitation. Create new tests only when requested or required by repository policy/acceptance criteria.

### V4

Use a build only for changes whose integration can fail beyond Dart analysis, such as native plugins/configuration. Build the affected target only.

Examples:

```bash
flutter build apk --debug
flutter build ios --simulator
```

Do not build Android + iOS by default.

### V5

Use a simulator/device only for behavior that depends on runtime/platform state. Verify the smallest scenario that exercises the changed path.

## Avoid ritual commands

Do not run these without evidence:

```text
flutter clean
pod deintegrate
pod install --repo-update
rm -rf Pods
rm -rf ~/.gradle/caches
```

A dependency edit may justify `flutter pub get`; an ordinary Dart edit does not.

## Common semantic escalations

Even if filenames look like ordinary Dart files, raise to V5 when the task changes:

- camera/microphone/location permission flow;
- deep/app/universal links;
- push notification receipt/tap behavior;
- app lifecycle/background execution;
- platform channels or plugin runtime behavior.

## Generated code

If source annotations/schema changed and the project uses code generation, run only the established generator command. Do not regenerate unrelated outputs if the repository supports a targeted generator.
