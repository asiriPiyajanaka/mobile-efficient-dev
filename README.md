# mobile-efficient-dev

A portable Agent Skill for **Flutter and React Native / Expo** development that aims to reduce model-visible context, noisy tool output, repeated verification, and unnecessary builds while preserving repository rules and risk-appropriate checks.

> The goal is not "run the fewest commands." It is **the least context and verification work that provides sufficient evidence for the change**.

## Status

**v0.2.0 — public preview**

The workflow is intentionally conservative: repository instructions, CI requirements, acceptance criteria, and explicit user requests always override the skill's efficiency defaults.

Token savings vary by agent, repository, task, failures, and tool-output behavior. The skill reduces common sources of context growth; it does not promise a fixed percentage reduction.

## What it does

- reads the smallest useful amount of code/context;
- searches for nearby reusable patterns before broad architecture reads;
- batches coherent edits before verification;
- classifies changes into verification levels **V0–V5**;
- runs only checks justified by the failure mode;
- keeps successful command logs out of model context;
- expands failed logs only when necessary;
- routes only repository rules relevant to the task/change surface;
- optionally enforces simple rules deterministically;
- avoids flagging unrelated legacy regex violations by default;
- avoids treating generic TypeScript as React Native without a mobile manifest.

It does **not** blindly skip tests, builds, or runtime checks.

## Structure

```text
mobile-efficient-dev/
├── SKILL.md
├── README.md
├── LICENSE
├── CHANGELOG.md
├── agents/
│   └── openai.yaml
├── scripts/
│   ├── plan.py
│   ├── rule_guard.py
│   └── run_quiet.py
├── references/
│   ├── context-budget.md
│   ├── flutter.md
│   ├── react-native.md
│   ├── rule-routing.md
│   └── verification-matrix.md
├── assets/
│   ├── AGENTS.example.md
│   └── mobile-agent-rules.example.json
├── evals/
│   ├── README.md
│   └── cases.json
└── tests/
```

## Requirements

The skill body itself has no third-party Python dependencies.

- Python 3.9+ for bundled helper scripts
- Git recommended for automatic change detection
- the target project's own Flutter/FVM or React Native/Expo toolchain for actual verification

## Install

### Codex — repository scoped

Copy the folder to:

```text
<repo>/.agents/skills/mobile-efficient-dev/
```

### Codex — user scoped

Copy it to:

```text
~/.agents/skills/mobile-efficient-dev/
```

Codex can also install skills from repositories through its skill installer workflow.

### Claude Code — project scoped

Copy it to:

```text
<repo>/.claude/skills/mobile-efficient-dev/
```

### Claude Code — personal

Copy it to:

```text
~/.claude/skills/mobile-efficient-dev/
```

The core `SKILL.md`, `scripts/`, `references/`, and `assets/` follow the Agent Skills open format. Product-specific behavior may still differ between agents.

## Normal workflow

```text
minimal context
→ relevant rules
→ coherent edit batch
→ task-local changed files
→ classify risk
→ minimum sufficient verification
→ escalate only on evidence
```

### Inspect a verification plan

From the app/repository root:

```bash
python3 /path/to/mobile-efficient-dev/scripts/plan.py \
  --task "add camera permission flow on profile screen" \
  --files lib/features/profile/profile_screen.dart android/app/src/main/AndroidManifest.xml
```

When `--files` is omitted, the script uses working-tree Git changes. Prefer explicit task files if the repository already contains unrelated modifications.

### Keep noisy output concise

```bash
python3 /path/to/mobile-efficient-dev/scripts/run_quiet.py \
  --label flutter-analyze -- flutter analyze
```

Successful logs are deleted by default. Failed logs remain under the OS temporary directory so the agent can inspect only the relevant section.

### Optional deterministic rules

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
python3 /path/to/mobile-efficient-dev/scripts/rule_guard.py route \
  --task "update login form" \
  --files lib/features/login/login_screen.dart

python3 /path/to/mobile-efficient-dev/scripts/rule_guard.py check \
  --files lib/features/login/login_screen.dart
```

By default, regex rules check changed lines rather than failing on old violations elsewhere in a touched file. Use `"scope": "file"` on rules that require whole-file compliance.

## Verification levels

| Level | Purpose | Typical examples |
|---|---|---|
| V0 | No runtime check | docs/comments |
| V1 | Lightweight local check | formatting, asset/config integrity |
| V2 | Static | localized UI, presentation code |
| V3 | Targeted behavior | state, logic, API mapping, navigation |
| V4 | Build/integration | native modules, Gradle/Pods, native-affecting deps |
| V5 | Focused runtime | permissions, camera, deep links, notifications, lifecycle |

## Test the skill helpers

```bash
python3 -m unittest discover -s tests -v
```

The helper tests cover risk classification, deletion detection, mobile platform detection, rule scoping, and quiet command behavior.

## Security / privacy notes

`run_quiet.py` captures command output before summarizing it. Passing logs are deleted by default; failed logs remain in the OS temporary directory and can contain whatever the underlying tool printed, including potentially sensitive values. Inspect and remove those logs when working with sensitive build environments.

The skill never installs packages, resets caches, runs cleanup commands, or modifies `.mobile-agent-rules.json` on its own.

## Distribution

For simple public use, a GitHub repository containing this skill is enough for people to copy/install it into supported coding agents. OpenAI currently recommends packaging reusable skills as a **plugin** when you want broader installable distribution across ChatGPT/Codex surfaces.

## License

MIT. See `LICENSE`.
