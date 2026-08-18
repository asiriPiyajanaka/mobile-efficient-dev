#!/usr/bin/env python3
"""Run a command while keeping successful/noisy output out of model context."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import subprocess
import tempfile
import time
from datetime import datetime
from pathlib import Path

ERROR_RE = re.compile(
    r"(error|exception|failed|failure|fatal|undefined|cannot find|not found|"
    r"type mismatch|syntax|assert|✗|×|FAILED)",
    re.IGNORECASE,
)


def log_dir_for(cwd: Path) -> Path:
    key = hashlib.sha1(str(cwd).encode("utf-8")).hexdigest()[:10]
    path = Path(tempfile.gettempdir()) / "mobile-development-skills" / key / "logs"
    path.mkdir(parents=True, exist_ok=True)
    return path


def _diagnostic(log_path: Path, max_lines: int) -> list[str]:
    try:
        lines = log_path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return []

    matches = [line for line in lines if ERROR_RE.search(line)]
    excerpt = matches[:max_lines]
    if not excerpt:
        excerpt = lines[-max_lines:]
    else:
        remaining = max_lines - len(excerpt)
        if remaining > 0:
            tail = [line for line in lines[-remaining:] if line not in excerpt]
            excerpt.extend(tail[:remaining])

    out: list[str] = []
    for line in excerpt:
        if len(line) > 500:
            line = line[:497] + "..."
        out.append(line)
    return out


def main() -> int:
    parser = argparse.ArgumentParser(
        usage="%(prog)s --label NAME [--max-lines N] [--timeout SEC] [--keep-success-log] -- command [args...]"
    )
    parser.add_argument("--label", required=True)
    parser.add_argument("--cwd", default=".")
    parser.add_argument("--max-lines", type=int, default=24)
    parser.add_argument("--timeout", type=float, default=0.0, help="0 disables timeout.")
    parser.add_argument("--keep-success-log", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        parser.error("missing command after --")

    cwd = Path(args.cwd).resolve()
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S-%f")
    safe_label = re.sub(r"[^a-zA-Z0-9_.-]+", "-", args.label).strip("-") or "check"
    log_path = log_dir_for(cwd) / f"{stamp}-{safe_label}.log"

    started = time.monotonic()
    code = 0
    timed_out = False
    proc = None
    try:
        with log_path.open("w", encoding="utf-8", errors="replace") as log:
            proc = subprocess.Popen(
                command,
                cwd=cwd,
                stdout=log,
                stderr=subprocess.STDOUT,
                text=True,
                env=os.environ.copy(),
            )
            try:
                code = proc.wait(timeout=args.timeout if args.timeout > 0 else None)
            except subprocess.TimeoutExpired:
                timed_out = True
                proc.kill()
                proc.wait()
                code = 124
    except FileNotFoundError:
        try:
            log_path.unlink(missing_ok=True)
        except OSError:
            pass
        print(f"CHECK {args.label} ERROR command-not-found={command[0]}")
        return 127
    except KeyboardInterrupt:
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=2)
            except Exception:
                try:
                    proc.kill()
                except Exception:
                    pass
        print(f"CHECK {args.label} INTERRUPTED")
        return 130

    duration = time.monotonic() - started

    if code == 0:
        if args.keep_success_log:
            print(f"CHECK {args.label} PASS duration={duration:.1f}s log={log_path}")
        else:
            try:
                log_path.unlink(missing_ok=True)
            except OSError:
                pass
            print(f"CHECK {args.label} PASS duration={duration:.1f}s")
        return 0

    status = "TIMEOUT" if timed_out else "FAIL"
    print(f"CHECK {args.label} {status} exit={code} duration={duration:.1f}s log={log_path}")
    excerpt = _diagnostic(log_path, max(1, args.max_lines))
    if excerpt:
        print("diagnostic:")
        for line in excerpt:
            print(line)
    print("next=inspect only the relevant section of the full log if this diagnostic is insufficient")
    return code


if __name__ == "__main__":
    raise SystemExit(main())
