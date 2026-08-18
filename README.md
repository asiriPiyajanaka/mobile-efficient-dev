# mobile-development-skills

A token/context-aware development workflow skill for **Flutter and React Native / Expo** coding agents.

It is designed to reduce unnecessary model-visible context, command output, repeated verification, and builds while preserving repository rules and risk-appropriate checks.

> The goal is not "run the fewest commands." It is the least context and verification work that provides sufficient evidence for the change.

## Status

**v0.2.0 - public preview**

The workflow is intentionally conservative: repository instructions, CI requirements, acceptance criteria, and explicit user requests always override the skill's efficiency defaults.

Token savings vary by agent, repository, task, failures, and tool-output behavior. The skill reduces common sources of context growth; it does not promise a fixed percentage reduction.

## Why this exists

Coding agents often spend too much context and time on mobile app changes by reading broad repositories, reopening known files, running analyzers after each tiny edit, launching simulators for static changes, or pasting huge Gradle/Xcode logs into the conversation.

`mobile-development-skills` keeps the agent deliberate: inspect only enough context to act safely, batch coherent edits, classify the risk of the final change set, and verify at the lowest sufficient level.

It does not blindly skip tests, builds, or runtime checks.

## How it works

- reads the smallest useful amount of code/context;
- searches for nearby reusable patterns before broad architecture reads;
- batches coherent edits before verification;
- classifies changes into verification levels **V0-V5**;
- runs only checks justified by the failure mode;
- keeps successful command logs out of model context;
- expands failed logs only when necessary;
- routes only repository rules relevant to the task/change surface;
- optionally enforces simple rules deterministically;
- avoids flagging unrelated legacy regex violations by default;
- avoids treating generic TypeScript as React Native without a mobile manifest.

## Architecture

```text
Task
  ↓
Context Router
  ↓
Relevant Rule Router
  ↓
Implementation Batch
  ↓
Change Classifier
  ↓
Verification Planner
  ↓
Execution Governor
  ↓
Concise Result
```

The skill separates workflow from repository policy. Repository rules still define what the app allows; this skill decides how narrowly the agent should gather context and verify the requested change.

## Structure

```text
mobile-development-skills/
├── SKILL.md
├── README.md
├── LICENSE
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── agents/
├── scripts/
├── references/
├── assets/
├── examples/
├── evals/
├── tests/
└── .github/
```

## Requirements

The skill body itself has no third-party Python dependencies.

- Python 3.9+ for bundled helper scripts
- Git recommended for automatic change detection
- the target project's own Flutter/FVM or React Native/Expo toolchain for actual verification

## Installation

### Codex installation

Repository scoped:

```text
<repo>/.agents/skills/mobile-development-skills/
```

User scoped:

```text
~/.agents/skills/mobile-development-skills/
```

Codex can also install skills from repositories through its skill installer workflow.

### Claude Code installation

Project scoped:

```text
<repo>/.claude/skills/mobile-development-skills/
```

Personal:

```text
~/.claude/skills/mobile-development-skills/
```

The core `SKILL.md`, `scripts/`, `references/`, and `assets/` follow the Agent Skills open format. Product-specific behavior may still differ between agents.

## Usage examples

### Normal workflow

```text
minimal context
→ relevant rules
→ coherent edit batch
→ task-local changed files
→ classify risk
→ minimum sufficient verification
→ escalate only on evidence
```

### Flutter example

A localized spacing change in `lib/features/profile/widgets/profile_header.dart` usually maps to V2:

```bash
python3 /path/to/mobile-development-skills/scripts/plan.py \
  --platform flutter \
  --task "adjust profile header spacing" \
  --files lib/features/profile/widgets/profile_header.dart
```

Typical verification:

```bash
dart format lib/features/profile/widgets/profile_header.dart
python3 /path/to/mobile-development-skills/scripts/run_quiet.py \
  --label flutter-analyze -- flutter analyze
```

It should not automatically trigger `flutter test`, `flutter build`, or `flutter run`.

### React Native example

A reducer or mapping change in a React Native workspace usually maps to V3:

```bash
python3 /path/to/mobile-development-skills/scripts/plan.py \
  --platform react-native \
  --task "fix checkout state transition" \
  --files apps/mobile/src/features/checkout/checkoutReducer.ts
```

Typical verification uses existing project scripts and the smallest relevant test:

```bash
python3 /path/to/mobile-development-skills/scripts/run_quiet.py \
  --label typecheck -- pnpm typecheck
python3 /path/to/mobile-development-skills/scripts/run_quiet.py \
  --label checkout-test -- pnpm test checkoutReducer
```

Do not invent missing scripts or reinstall dependencies just because a file is TypeScript.

### Inspect a verification plan

From the app/repository root:

```bash
python3 /path/to/mobile-development-skills/scripts/plan.py \
  --task "add camera permission flow on profile screen" \
  --files lib/features/profile/profile_screen.dart android/app/src/main/AndroidManifest.xml
```

When `--files` is omitted, the script uses working-tree Git changes. Prefer explicit task files if the repository already contains unrelated modifications.

### Keep noisy output concise

```bash
python3 /path/to/mobile-development-skills/scripts/run_quiet.py \
  --label flutter-analyze -- flutter analyze
```

Successful logs are deleted by default. Failed logs remain under the OS temporary directory so the agent can inspect only the relevant section.

## Repository rule configuration

Keep repository rules separate from this skill. Put app-specific architecture, UI, navigation, state-management, API, native, and testing rules in small files such as:

```text
docs/engineering/architecture.md
docs/engineering/flutter-ui.md
docs/engineering/navigation.md
docs/engineering/native.md
```

Then route only the references relevant to the current task or changed paths.

## Deterministic rules example

Copy:

```text
assets/mobile-agent-rules.example.json
```

to:

```text
.mobile-agent-rules.json
```

Then:

```bash
python3 /path/to/mobile-development-skills/scripts/rule_guard.py route \
  --task "update login form" \
  --files lib/features/login/login_screen.dart

python3 /path/to/mobile-development-skills/scripts/rule_guard.py check \
  --files lib/features/login/login_screen.dart
```

By default, regex rules check changed lines rather than failing on old violations elsewhere in a touched file. Use `"scope": "file"` on rules that require whole-file compliance.

## Verification ladder

| Level | Purpose                 | Typical examples                                          |
| ----- | ----------------------- | --------------------------------------------------------- |
| V0    | No runtime check        | docs/comments                                             |
| V1    | Lightweight local check | formatting, asset/config integrity                        |
| V2    | Static                  | localized UI, presentation code                           |
| V3    | Targeted behavior       | state, logic, API mapping, navigation                     |
| V4    | Build/integration       | native modules, Gradle/Pods, native-affecting deps        |
| V5    | Focused runtime         | permissions, camera, deep links, notifications, lifecycle |

## Limitations

- The helper scripts are advisory. Agents must raise verification when task semantics, repository policy, or failures show higher risk.
- Regex rules are intentionally small and are not a replacement for a full lint framework.
- Platform detection depends on nearby manifests. Pass `--platform` when working in unusual monorepos.
- The skill cannot guarantee token savings; it reduces common sources of unnecessary context and command output.
- Runtime-sensitive features still require focused runtime/device verification when static checks cannot prove behavior.

## Development

The project intentionally avoids third-party Python dependencies. Keep helper scripts portable and focused.

Useful local commands:

```bash
python3 -m unittest discover -s tests -v
python3 scripts/plan.py --task "docs update" --files README.md
python3 scripts/run_quiet.py --label unit-tests -- python3 -m unittest discover -s tests
```

## Tests

```bash
python3 -m unittest discover -s tests -v
```

The helper tests cover risk classification, deletion detection, mobile platform detection, rule scoping, and quiet command behavior.

## Roadmap

- Add more behavior eval cases for Expo, FVM, and nested workspace layouts.
- Improve concise diagnostic extraction for common Flutter, Gradle, Xcode, ESLint, TypeScript, and Jest failures.
- Expand deterministic rule examples while keeping the checker intentionally small.
- Document measured benchmarks only after repeatable eval data exists.

## Contributing

See `CONTRIBUTING.md`.

## Security

`run_quiet.py` captures command output before summarizing it. Passing logs are deleted by default; failed logs remain in the OS temporary directory and can contain whatever the underlying tool printed, including potentially sensitive values. Inspect and remove those logs when working with sensitive build environments.

The skill never installs packages, resets caches, runs cleanup commands, or modifies `.mobile-agent-rules.json` on its own.

Report vulnerabilities privately. See `SECURITY.md`.

## Distribution

For simple public use, a GitHub repository containing this skill is enough for people to copy/install it into supported coding agents. OpenAI currently recommends packaging reusable skills as a **plugin** when you want broader installable distribution across ChatGPT/Codex surfaces.

## License

MIT. See `LICENSE`.
