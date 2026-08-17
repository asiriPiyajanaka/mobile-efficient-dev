# Context budget

The goal is to reduce model-visible context while preserving enough evidence to work correctly.

## Context acquisition order

1. applicable repository instructions;
2. target file/module;
3. search for an existing equivalent pattern/component;
4. nearest implementation that establishes the convention;
5. only then inspect architecture/docs if ambiguity remains.

## Stop conditions

Stop gathering context when all are known:

- where the change belongs;
- which existing component/pattern to reuse;
- what public interface/state contract is affected;
- which project rules apply;
- what verification level is required.

Do not keep reading "for completeness."

## Prefer search over broad reads

Good:

```bash
rg "AppButton|PrimaryButton" lib src
rg "GoRoute|navigation.navigate" <feature-path>
git diff --stat
git diff -- <changed-file>
```

Avoid reading entire directories or large generated files when a targeted search answers the question.

## Task-local change scope

A dirty working tree may contain changes unrelated to the current task. Keep a short list of files actually touched by this task and use that list for planning/rule checks. Do not let unrelated native/config changes force broader verification.

## Command-output budget

For successful checks, a one-line result is normally enough. Full successful output is usually unnecessary.

For failures:

1. show matching error/exception/failure lines;
2. include a small tail if necessary;
3. keep the full failure log path;
4. read a narrow log section only when the concise diagnostic is insufficient.

## Reuse context

Do not reopen a file just because a later step mentions it. Reopen only if:

- it changed since last read;
- exact line context is needed for a patch/failure;
- a new dependency/contract question arose.

## Diff discipline

Use task-local changed-file names and scoped diffs first. Avoid repeatedly injecting the complete repository diff after every edit.
