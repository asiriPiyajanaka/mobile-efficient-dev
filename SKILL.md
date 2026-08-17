---
name: mobile-efficient-dev
description: Develop Flutter and React Native apps with minimum sufficient context and verification. Use for implementation, fixes, refactors, UI, state, navigation, dependencies, native config, builds, tests, or post-change checks when you want to reduce agent token/tool overhead without weakening repository rules. Classify risk, load only relevant rules, batch edits, and escalate checks only when evidence requires it. Do not use for non-Flutter/non-React-Native repositories.
license: MIT
compatibility: Agent Skills-compatible coding agent. Bundled scripts require Python 3.9+; Git is recommended for change detection. Uses the target repository's existing Flutter/FVM or React Native/Expo toolchain rather than installing its own mobile dependencies.
metadata:
  version: "0.2.0"
---

# Mobile Efficient Development

Optimize for **minimum sufficient work**, not minimum safety.

Never skip a check explicitly required by the user, repository guidance (`AGENTS.md`, `CLAUDE.md`, CI policy), or acceptance criteria. Project rules override this skill when they require stricter validation.

The bundled scripts are advisory helpers. Do not let a classifier override stronger evidence from the task, repository, or failing diagnostics.

## Core loop

For every Flutter or React Native task:

1. **Acquire minimal context**
   - Read applicable repository guidance once, starting with the closest instructions.
   - Search before reading. Prefer targeted search to opening broad directories.
   - Inspect the target module and the nearest existing implementation pattern.
   - Stop when there is enough evidence to implement consistently.
   - Do not reread unchanged files unless a new question requires it.

2. **Route relevant rules**
   - If `.mobile-agent-rules.json` exists, use `scripts/rule_guard.py route`.
   - Load only references returned for the task/change surface.
   - Otherwise use applicable `AGENTS.md`/`CLAUDE.md` and nearby conventions.
   - Prefer deterministic checks for simple rules instead of repeatedly explaining them to the model.

3. **Batch coherent edits**
   - Make a coherent implementation batch before verification.
   - Do not format/analyze/test after every micro-edit.
   - Run an intermediate check only when it unblocks implementation or prevents expensive wrong-direction work.

4. **Track this task's change surface**
   - Prefer a task-local list of files you actually edited/created/deleted.
   - Pass those paths with `--files` to `plan.py` and `rule_guard.py` when the working tree contains unrelated user/agent changes.
   - Fall back to automatic Git detection only when repository-wide working-tree changes represent this task.

5. **Classify the final change set**
   - Run `scripts/plan.py` after the coherent edit batch.
   - Treat its level as a baseline, not a verdict.
   - Raise the level when task semantics or repository policy imply a stronger failure mode.

6. **Verify at the lowest sufficient level**
   - Run only checks required by the selected level and repository policy.
   - Prefer targeted tests to broad suites.
   - Prefer one affected platform/build target to all targets unless the change is truly cross-platform.
   - For noisy commands, use `scripts/run_quiet.py` so successful output does not enter model context.

7. **Escalate only on evidence**
   - Failure flow: concise diagnostic → relevant fix → rerun only invalidated check.
   - Do not rerun a successful check unless relevant code changed afterward.
   - Do not run `flutter clean`, reinstall Pods/node modules, reset caches, or rebuild everything without evidence of stale state.

## Verification ladder

- **V0 — None:** docs/comments/non-runtime documentation only.
- **V1 — Lightweight local check:** changed-file format/syntax, asset integrity, or config sanity where relevant.
- **V2 — Static:** V1 as relevant + analyzer/lint/type check. Default for localized UI/presentation changes.
- **V3 — Targeted behavior:** V2 + smallest relevant existing test or focused behavior check. Use for state, business logic, data mapping, navigation, API/storage logic, dependency changes, and test changes.
- **V4 — Build/integration:** V2/V3 as relevant + one narrow platform build/integration check. Use for native modules/plugins, build config, generated/native bindings, or native-affecting dependency changes.
- **V5 — Runtime:** V4 + focused simulator/device/manual smoke verification. Use for permissions, camera, deep links, push notifications, lifecycle/background behavior, platform channels, or behavior that cannot be validated statically.

Read `references/verification-matrix.md` only when classification is ambiguous.

## Output and token discipline

- Do not dump successful build/analyzer/test logs into context.
- On success, keep only check name, PASS, and duration.
- On failure, show actionable diagnostics first; inspect the full log only if necessary.
- Do not paste large diffs when changed paths, `git diff --stat`, or a scoped diff answers the question.
- Avoid broad repository summaries unless architecture discovery is genuinely required.
- Do not narrate routine tool usage at length; report decisions and meaningful failures.

Example:

```bash
python3 <skill-dir>/scripts/run_quiet.py --label analyze -- flutter analyze
```

By default, successful logs are deleted. Failed logs remain in the OS temp directory for selective inspection and may contain sensitive command output.

## Platform adapters

Read only the adapter relevant to the current app:

- Flutter: `references/flutter.md`
- React Native / Expo: `references/react-native.md`

If platform detection returns `unknown`, do not guess from generic TypeScript/JavaScript alone. Use the repository manifest or pass `--platform` explicitly.

## Rule enforcement

If the project wants reusable deterministic rules, copy `assets/mobile-agent-rules.example.json` to the repository root as `.mobile-agent-rules.json`, customize it, and keep rule references small and path-scoped.

Use:

```bash
python3 <skill-dir>/scripts/rule_guard.py route --task "<short task description>" --files <task-files...>
python3 <skill-dir>/scripts/rule_guard.py check --files <task-files...>
```

The rule file is optional. Do not create or modify it unless the user asks or repository policy allows it.

Regex guards default to `scope: changed_lines` so pre-existing violations elsewhere in a touched file do not block adoption. Set a rule to `scope: file` when the entire file must comply.

## Completion report

Keep the final verification report compact:

```text
Verification: V2
Rules: UI-001, ARCH-002 (pass)
Local/static checks: pass
Tests/build/runtime: not required
```

If a higher level could not run because the environment lacks a simulator, SDK, credentials, or platform toolchain, state that limitation. Do not substitute unrelated broad checks merely to claim verification.
