#!/usr/bin/env python3
"""Route relevant repository rules and enforce deterministic regex rules on changed code."""

from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
import sys
from pathlib import Path

from plan import changed_files, classify_files

DEFAULT_CONFIG = ".mobile-agent-rules.json"
HUNK_RE = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@")


def brace_expand(pattern: str) -> list[str]:
    m = re.search(r"\{([^{}]+)\}", pattern)
    if not m:
        return [pattern]
    out: list[str] = []
    for choice in m.group(1).split(","):
        out.extend(brace_expand(pattern[:m.start()] + choice + pattern[m.end():]))
    return out


def path_matches(path: str, patterns: list[str] | None) -> bool:
    if not patterns:
        return True
    path = path.replace("\\", "/")
    for raw in patterns:
        for pattern in brace_expand(raw.replace("\\", "/")):
            candidates = {pattern}
            if "/**/" in pattern:
                candidates.add(pattern.replace("/**/", "/"))
            if any(fnmatch.fnmatch(path, p) for p in candidates):
                return True
    return False


def applicable_path(path: str, rule: dict) -> bool:
    if not path_matches(path, rule.get("paths")):
        return False
    if rule.get("exclude_paths") and path_matches(path, rule["exclude_paths"]):
        return False
    return True


def load_rules(config_path: Path) -> list[dict]:
    try:
        data = json.loads(config_path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return []
    except json.JSONDecodeError as e:
        print(f"RULE_CONFIG invalid-json file={config_path} line={e.lineno}", file=sys.stderr)
        raise SystemExit(2)
    rules = data.get("rules", [])
    if not isinstance(rules, list):
        print("RULE_CONFIG invalid: 'rules' must be an array", file=sys.stderr)
        raise SystemExit(2)
    return [r for r in rules if isinstance(r, dict) and r.get("id")]


def route_rules(rules: list[dict], files: list[str], task: str) -> list[dict]:
    categories = set(classify_files(files, task).get("categories", []))
    task_low = task.lower()
    matched: list[dict] = []

    for rule in rules:
        path_hit = any(applicable_path(f, rule) for f in files) if files else not rule.get("paths")
        keyword_hit = any(str(k).lower() in task_low for k in rule.get("task_keywords", []))
        category_hit = bool(categories & set(rule.get("categories", [])))

        selectors_present = bool(rule.get("task_keywords") or rule.get("categories"))
        selector_hit = (keyword_hit or category_hit) if selectors_present else True

        # A task keyword can route a rule before files exist; otherwise honor path scope.
        if (path_hit and selector_hit) or (not files and keyword_hit):
            matched.append(rule)

    return matched


def _git(root: Path, args: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )


def changed_line_numbers(root: Path, rel: str) -> set[int] | None:
    """Return changed new-file line numbers, or None to mean scan the whole file.

    Untracked/new files are scanned in full. Existing tracked files default to changed
    lines only so legacy violations elsewhere in the same file do not block adoption.
    """
    tracked = _git(root, ["ls-files", "--error-unmatch", "--", rel])
    if tracked.returncode != 0:
        return None

    diff = _git(root, ["diff", "--unified=0", "HEAD", "--", rel])
    if diff.returncode != 0:
        # Repositories without HEAD or unusual git state: safest fallback is whole file.
        return None

    lines: set[int] = set()
    for raw in diff.stdout.splitlines():
        match = HUNK_RE.match(raw)
        if not match:
            continue
        start = int(match.group(1))
        count = int(match.group(2) or "1")
        if count > 0:
            lines.update(range(start, start + count))
    return lines


def _match_lines(text: str, match: re.Match[str]) -> set[int]:
    start_line = text.count("\n", 0, match.start()) + 1
    end_offset = max(match.start(), match.end() - 1)
    end_line = text.count("\n", 0, end_offset) + 1
    return set(range(start_line, end_line + 1))


def check_rules(rules: list[dict], root: Path, files: list[str], max_violations: int) -> int:
    violations: list[tuple[str, str, str, int, str, str]] = []
    error_count = 0
    line_cache: dict[str, set[int] | None] = {}

    for rule in rules:
        patterns = rule.get("forbid_regex", [])
        if not patterns:
            continue
        compiled: list[re.Pattern[str]] = []
        for pattern in patterns:
            try:
                compiled.append(re.compile(pattern, re.MULTILINE))
            except re.error as e:
                print(f"RULE_CONFIG invalid-regex id={rule['id']} error={e}", file=sys.stderr)
                return 2

        scope = str(rule.get("scope", "changed_lines")).lower()
        if scope not in {"changed_lines", "file"}:
            print(f"RULE_CONFIG invalid-scope id={rule['id']} scope={scope}", file=sys.stderr)
            return 2

        for rel in files:
            if not applicable_path(rel, rule):
                continue
            path = root / rel
            if not path.is_file():
                # Deleted paths are relevant to planning, but there is no current content to scan.
                continue
            try:
                if path.stat().st_size > 2_000_000:
                    continue
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue

            changed_lines: set[int] | None = None
            if scope == "changed_lines":
                if rel not in line_cache:
                    line_cache[rel] = changed_line_numbers(root, rel)
                changed_lines = line_cache[rel]

            split_lines = text.splitlines()
            for rx in compiled:
                for match in rx.finditer(text):
                    matched_lines = _match_lines(text, match)
                    if scope == "changed_lines" and changed_lines is not None and not (matched_lines & changed_lines):
                        continue

                    line_no = min(matched_lines)
                    severity = str(rule.get("severity", "error")).lower()
                    excerpt = split_lines[line_no - 1].strip() if 0 < line_no <= len(split_lines) else ""
                    if len(excerpt) > 180:
                        excerpt = excerpt[:177] + "..."
                    violations.append(
                        (rule["id"], severity, rel, line_no, rule.get("description", ""), excerpt)
                    )
                    if severity == "error":
                        error_count += 1
                    if len(violations) >= max_violations:
                        break
                if len(violations) >= max_violations:
                    break
            if len(violations) >= max_violations:
                break
        if len(violations) >= max_violations:
            break

    if not violations:
        print(f"RULE_CHECK PASS rules={len(rules)} files={len(files)}")
        return 0

    print(f"RULE_CHECK FAIL violations={len(violations)} errors={error_count}")
    for rid, severity, rel, line_no, desc, excerpt in violations:
        print(f"{rid} [{severity}] {rel}:{line_no} {desc}")
        if excerpt:
            print(f"  {excerpt}")
    if len(violations) >= max_violations:
        print(f"truncated=true max_violations={max_violations}")
    return 1 if error_count else 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["route", "check"])
    parser.add_argument("--root", default=".")
    parser.add_argument("--config", default=DEFAULT_CONFIG)
    parser.add_argument("--task", default="")
    parser.add_argument("--files", nargs="*")
    parser.add_argument("--max-violations", type=int, default=40)
    args = parser.parse_args()

    root = Path(args.root).resolve()
    config = Path(args.config)
    if not config.is_absolute():
        config = root / config

    if not config.exists():
        print(f"RULE_{args.mode.upper()} none config=missing")
        return 0

    rules = load_rules(config)
    files = args.files if args.files is not None else changed_files(root)

    if args.mode == "route":
        matched = route_rules(rules, files, args.task)
        if not matched:
            print(f"RULE_ROUTE none rules={len(rules)} changed={len(files)}")
            return 0
        refs: list[str] = []
        print(f"RULE_ROUTE matched={len(matched)} changed={len(files)}")
        for rule in matched:
            severity = rule.get("severity", "error")
            rrefs = rule.get("references", [])
            refs.extend(rrefs)
            ref_text = ",".join(rrefs) if rrefs else "none"
            print(f"{rule['id']} [{severity}] refs={ref_text} {rule.get('description', '')}")
        unique_refs = list(dict.fromkeys(refs))
        if unique_refs:
            print("read_only=" + ",".join(unique_refs))
        return 0

    return check_rules(rules, root, files, args.max_violations)


if __name__ == "__main__":
    raise SystemExit(main())
