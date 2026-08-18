# Verification Plan Examples

These examples show the intended decision shape. Repository instructions and explicit user requests can require stricter verification.

## Documentation only

```text
task: update README installation wording
files: README.md
level: V0
run: no runtime verification
skip: format/analyze/tests/build/runtime
```

## Flutter localized UI

```text
task: adjust profile header spacing
files: lib/features/profile/widgets/profile_header.dart
level: V2
run: dart format on changed Dart file, flutter analyze
skip: flutter test, flutter build, simulator/device
```

## Flutter permission flow

```text
task: request camera permission from profile screen
files:
  lib/features/profile/profile_screen.dart
  android/app/src/main/AndroidManifest.xml
level: V5
run: static checks, affected Android build/config check, focused runtime permission smoke
skip: unrelated iOS build unless the change also affects iOS
```

## React Native state behavior

```text
task: fix checkout reducer transition
files: apps/mobile/src/features/checkout/checkoutReducer.ts
level: V3
run: existing type/lint check and smallest relevant reducer test
skip: native builds and Metro cache resets
```

## React Native native config

```text
task: add Android app link intent filter
files: android/app/src/main/AndroidManifest.xml
level: V5
run: static checks, narrow Android build/config check, focused deep-link runtime smoke
skip: iOS build unless affected
```
