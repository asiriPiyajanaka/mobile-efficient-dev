# Rule routing and deterministic guards

Repository rules should answer **what must be true**. This skill answers **the cheapest way to implement and verify it**.

## Keep global guidance small

Use `AGENTS.md` / `CLAUDE.md` for high-value persistent rules and routing instructions. Put detailed area-specific guidance close to the relevant code or in referenced docs.

Do not duplicate the same long rules in this skill and repository guidance.

## Optional `.mobile-agent-rules.json`

This skill supports a zero-dependency JSON rule index for two jobs:

1. route only relevant rule references into context;
2. check simple forbidden patterns deterministically on task-touched files.

Each rule may contain:

```json
{
  "id": "UI-001",
  "description": "Use AppButton rather than raw ElevatedButton.",
  "severity": "error",
  "scope": "changed_lines",
  "paths": ["lib/**/*.dart"],
  "exclude_paths": ["lib/design_system/**"],
  "categories": ["ui"],
  "task_keywords": ["button", "form"],
  "references": ["docs/engineering/ui.md"],
  "forbid_regex": ["\\bElevatedButton\\s*\\("]
}
```

All fields except `id` are optional.

### Scope

- `changed_lines` (default): report a regex match only when it overlaps a Git-changed line. This reduces noise from legacy violations elsewhere in a touched file.
- `file`: scan the entire current file. Use when whole-file compliance is required.

Untracked/new files are scanned in full. In repositories with unrelated uncommitted changes, prefer explicit `--files` for the current task.

### Routing

```bash
python3 <skill-dir>/scripts/rule_guard.py route \
  --task "add submit button to signup form" \
  --files lib/features/signup/signup_screen.dart
```

The script returns matching rule IDs and reference paths. Read only those references.

### Checking

```bash
python3 <skill-dir>/scripts/rule_guard.py check \
  --files lib/features/signup/signup_screen.dart
```

## What to encode deterministically

Good candidates:

- forbidden raw UI primitives when a design-system wrapper is required;
- forbidden imports across architecture layers;
- disallowed direct API/client access from presentation code;
- prohibited debug logging in production paths;
- filename/path conventions expressible as regex/path rules.

Do not force nuanced architectural judgement into brittle regex. Use a referenced rule document for cases requiring reasoning.

## Rule precedence

User request and higher-priority safety/policy instructions remain authoritative. Repository rules should not be silently weakened by this skill.
