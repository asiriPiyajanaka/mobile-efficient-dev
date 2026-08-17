#!/usr/bin/env python3
"""Classify changed Flutter/React Native files into a minimum verification level."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Iterable

LEVELS = {"V0": 0, "V1": 1, "V2": 2, "V3": 3, "V4": 4, "V5": 5}

TEXT_DOC_EXTS = {".md", ".mdx", ".txt", ".rst", ".adoc"}
RUNTIME_ASSET_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg", ".riv", ".lottie",
    ".ttf", ".otf", ".woff", ".woff2", ".mp3", ".wav", ".m4a", ".mp4", ".mov",
}
CODE_EXTS = {
    ".dart", ".ts", ".tsx", ".js", ".jsx", ".mjs", ".cjs", ".kt", ".kts",
    ".java", ".swift", ".m", ".mm", ".h", ".cpp", ".cc",
}
NATIVE_NAMES = {
    "androidmanifest.xml", "info.plist", "podfile", "podfile.lock",
    "gradle.properties", "settings.gradle", "settings.gradle.kts",
    "build.gradle", "build.gradle.kts", "appdelegate.swift", "appdelegate.m",
    "mainactivity.kt", "mainactivity.java", "app.json", "app.config.js",
    "app.config.ts", "expo-module.config.json",
}
DEPENDENCY_NAMES = {
    "pubspec.yaml", "pubspec.lock", "package.json", "package-lock.json",
    "yarn.lock", "pnpm-lock.yaml", "npm-shrinkwrap.json",
}

RUNTIME_KEYWORDS = {
    "permission", "permissions", "camera", "microphone", "location", "geolocation",
    "deep_link", "deeplink", "app_link", "applink", "universal_link",
    "notification", "notifications", "push", "background", "lifecycle",
    "platform_channel", "methodchannel", "method_channel",
}
LOGIC_SEGMENTS = {
    "bloc", "cubit", "provider", "providers", "riverpod", "state", "store",
    "redux", "saga", "domain", "usecase", "use_case", "service", "services",
    "repository", "repositories", "datasource", "data_source", "api", "network",
    "storage", "serializer", "mapper", "mappers",
}
UI_SEGMENTS = {
    "screen", "screens", "page", "pages", "widget", "widgets", "component",
    "components", "view", "views", "presentation", "ui",
}
NAV_SEGMENTS = {"router", "routers", "route", "routes", "navigation", "navigator"}
TEST_MARKERS = {"test", "tests", "__tests__", "integration_test", "integration-tests", "e2e"}

TASK_V5 = (
    "permission", "camera", "microphone", "location", "deep link", "deeplink",
    "universal link", "app link", "push notification", "background",
    "lifecycle", "platform channel", "methodchannel", "method channel",
)
TASK_V4 = (
    "native module", "native plugin", "podfile", "gradle", "androidmanifest",
    "info.plist", "xcode", "cocoapods", "autolinking", "config plugin",
)
TASK_V3 = (
    "business logic", "state management", "bloc", "cubit", "riverpod",
    "redux", "api mapping", "serialization", "storage", "navigation", "routing",
    "dependency", "package upgrade", "package update",
)


def _run_git(args: list[str], cwd: Path) -> list[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if proc.returncode != 0:
        return []
    return [line.strip().replace("\\", "/") for line in proc.stdout.splitlines() if line.strip()]


def changed_files(root: Path) -> list[str]:
    """Return tracked, staged, deleted, renamed, and untracked working-tree paths."""
    tracked = _run_git(["diff", "--name-only", "--diff-filter=ACMRD", "HEAD"], root)
    staged = _run_git(["diff", "--cached", "--name-only", "--diff-filter=ACMRD"], root)
    untracked = _run_git(["ls-files", "--others", "--exclude-standard"], root)
    return sorted(set(tracked + staged + untracked))


def _segments(path: str) -> set[str]:
    p = path.lower().replace("\\", "/")
    parts: list[str] = []
    for piece in p.replace("-", "_").split("/"):
        stem = piece.rsplit(".", 1)[0]
        parts.extend(stem.split("_"))
        parts.append(stem)
    return set(parts)


def _is_docs_path(low: str) -> bool:
    return low.startswith("docs/") or "/docs/" in low


def classify_files(files: Iterable[str], task: str = "") -> dict:
    files = [f.replace("\\", "/") for f in files]
    categories: set[str] = set()
    reasons: list[str] = []
    max_level = 0

    if not files:
        return {
            "level": "V0",
            "risk": "NONE",
            "categories": [],
            "reasons": ["no changed files detected"],
            "files": [],
        }

    docs_only = True

    for f in files:
        p = Path(f)
        low = f.lower()
        name = p.name.lower()
        seg = _segments(f)
        suffix = p.suffix.lower()
        docs_path = _is_docs_path(low)
        is_text_doc = suffix in TEXT_DOC_EXTS or docs_path

        if not is_text_doc:
            docs_only = False

        if is_text_doc:
            categories.add("docs")

        if suffix in RUNTIME_ASSET_EXTS and not docs_path:
            categories.add("asset")
            max_level = max(max_level, 1)

        if (
            name in NATIVE_NAMES
            or low.startswith(("android/", "ios/"))
            or "/android/" in low
            or "/ios/" in low
            or low.endswith(".entitlements")
            or low.endswith(".xcconfig")
        ):
            categories.add("native")
            max_level = max(max_level, 4)

        if name in DEPENDENCY_NAMES:
            categories.add("dependency")
            max_level = max(max_level, 3)

        if seg & TEST_MARKERS or name.endswith(
            ("_test.dart", ".test.ts", ".test.tsx", ".spec.ts", ".spec.tsx", ".test.js", ".spec.js")
        ):
            categories.add("test")
            max_level = max(max_level, 3)

        if seg & NAV_SEGMENTS:
            categories.add("navigation")
            max_level = max(max_level, 3)

        if seg & LOGIC_SEGMENTS:
            categories.add("logic")
            max_level = max(max_level, 3)

        if seg & UI_SEGMENTS:
            categories.add("ui")
            max_level = max(max_level, 2)

        normalized = low.replace("-", "_")
        if any(k in normalized for k in RUNTIME_KEYWORDS):
            categories.add("runtime_sensitive")
            max_level = max(max_level, 5)

        if suffix in CODE_EXTS and max_level < 2:
            categories.add("code")
            max_level = max(max_level, 2)

    if docs_only:
        max_level = 0
        reasons.append("only documentation/non-runtime docs content changed")

    task_low = task.lower()
    if task_low:
        if any(k in task_low for k in TASK_V5):
            categories.add("runtime_sensitive")
            max_level = max(max_level, 5)
            reasons.append("task semantics require runtime/platform behavior verification")
        elif any(k in task_low for k in TASK_V4):
            categories.add("native")
            max_level = max(max_level, 4)
            reasons.append("task semantics affect native/build integration")
        elif any(k in task_low for k in TASK_V3):
            categories.add("logic")
            max_level = max(max_level, 3)
            reasons.append("task semantics affect behavior/logic")

    if "native" in categories and max_level >= 4:
        reasons.append("native/build configuration changed")
    if "dependency" in categories:
        reasons.append("dependency manifest/lockfile changed; native dependency changes may require V4")
    if {"logic", "navigation", "test"} & categories:
        reasons.append("behavioral code or tests changed")
    if "asset" in categories and max_level == 1:
        reasons.append("runtime asset changed; perform a lightweight integrity check and visual verification only when needed")
    if "ui" in categories and max_level == 2:
        reasons.append("localized presentation change")
    if "code" in categories and max_level == 2 and not reasons:
        reasons.append("code changed without higher-risk signals")

    level = f"V{max_level}"
    risk = {
        0: "LOW",
        1: "LOW",
        2: "LOW",
        3: "MEDIUM",
        4: "HIGH",
        5: "HIGH",
    }[max_level]

    return {
        "level": level,
        "risk": risk,
        "categories": sorted(categories),
        "reasons": reasons,
        "files": files,
    }


def _manifest_platform(directory: Path) -> tuple[bool, bool]:
    flutter = False
    rn = False

    pubspec = directory / "pubspec.yaml"
    if pubspec.exists():
        try:
            text = pubspec.read_text(encoding="utf-8", errors="ignore")
            flutter = "flutter:" in text or "sdk: flutter" in text
        except OSError:
            pass

    package = directory / "package.json"
    if package.exists():
        try:
            data = json.loads(package.read_text(encoding="utf-8"))
            deps: dict = {}
            for key in ("dependencies", "devDependencies", "peerDependencies"):
                value = data.get(key, {})
                if isinstance(value, dict):
                    deps.update(value)
            rn = "react-native" in deps or "expo" in deps
        except (OSError, json.JSONDecodeError):
            pass

    return flutter, rn


def _candidate_manifest_dirs(root: Path, files: Iterable[str]) -> list[Path]:
    dirs = {root}
    for rel in files:
        current = (root / rel).parent.resolve()
        while True:
            try:
                current.relative_to(root)
            except ValueError:
                break
            dirs.add(current)
            if current == root:
                break
            current = current.parent
    return sorted(dirs, key=lambda p: len(p.parts), reverse=True)


def detect_platform(root: Path, files: Iterable[str]) -> str:
    """Detect Flutter/RN from nearby manifests; do not infer RN from generic TS/JS."""
    flutter = False
    rn = False
    for directory in _candidate_manifest_dirs(root, files):
        f, r = _manifest_platform(directory)
        flutter = flutter or f
        rn = rn or r

    if flutter and rn:
        return "mixed"
    if flutter:
        return "flutter"
    if rn:
        return "react-native"
    return "unknown"


def actions_for(level: str) -> tuple[list[str], list[str]]:
    n = LEVELS[level]
    all_actions = [
        ("lightweight-local-check", 1),
        ("static-analysis", 2),
        ("targeted-behavior", 3),
        ("narrow-build/integration", 4),
        ("focused-runtime", 5),
    ]
    required = [name for name, min_level in all_actions if n >= min_level]
    skipped = [name for name, min_level in all_actions if n < min_level]
    return required, skipped


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default=".", help="Repository/app root.")
    parser.add_argument("--task", default="", help="Short task description for semantic escalation.")
    parser.add_argument("--platform", choices=["flutter", "react-native", "mixed", "unknown"])
    parser.add_argument("--files", nargs="*", help="Explicit changed files; otherwise read git changes.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    files = args.files if args.files is not None else changed_files(root)
    result = classify_files(files, args.task)
    result["platform"] = args.platform or detect_platform(root, files)
    required, skipped = actions_for(result["level"])
    result["required"] = required
    result["skipped"] = skipped

    if args.json:
        print(json.dumps(result, indent=2))
        return 0

    cats = ",".join(result["categories"]) or "none"
    req = ",".join(required) or "none"
    skip = ",".join(skipped) or "none"
    print(
        f"MOBILE_PLAN platform={result['platform']} level={result['level']} "
        f"risk={result['risk']} changed={len(result['files'])} categories={cats}"
    )
    print(f"required={req}")
    print(f"skip_by_default={skip}")
    for reason in result["reasons"][:4]:
        print(f"reason={reason}")
    if result["level"] in {"V4", "V5"}:
        print("scope=verify only the affected platform/scenario unless repo policy requires more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
