# React Native / Expo adapter

Use this reference only for React Native or Expo apps.

## Package manager

Infer the repository's established package manager from guidance and lockfiles. Do not switch package managers.

Typical signals:

- `pnpm-lock.yaml` → pnpm
- `yarn.lock` → yarn
- `package-lock.json` → npm

Respect Turborepo/workspace filters when present; run checks in the smallest affected workspace when repository scripts support that.

## Verification examples

### V1

For JS/TS edits, use the existing formatter script/config on changed files. Do not add Prettier just for this skill. For asset-only changes, perform only the relevant asset/path sanity check.

### V2

Prefer existing scripts:

```bash
npm run lint
npm run typecheck
```

or their yarn/pnpm equivalents.

Do not invent a `typecheck` script if the project does not define one. A direct `tsc --noEmit` is appropriate only when it matches the repo's TypeScript setup.

### V3

Run the smallest existing Jest/Vitest/unit test target related to the change. Do not run every workspace test by default.

### V4

Use native build verification when the change affects native modules, Pods, Gradle, app config that produces native changes, or native project files.

For Expo projects, distinguish managed/config-plugin changes from ordinary JS/TS changes. Do not prebuild/eject merely for routine UI work.

### V5

Use runtime verification for permissions, deep links, notifications, native lifecycle, camera/mic/location, or platform-dependent behavior.

## Avoid ritual resets

Do not run these without evidence:

```text
rm -rf node_modules
watchman watch-del-all
pod deintegrate
pod install --repo-update
./gradlew clean
reset Metro cache
```

Ordinary JS/TS changes do not justify dependency reinstall or cache clearing.

## Dependency changes

A pure JS dependency does not automatically require a native build. A dependency with native code/autolinking/config-plugin effects does.
