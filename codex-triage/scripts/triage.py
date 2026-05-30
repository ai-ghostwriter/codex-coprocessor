#!/usr/bin/env python3
"""
triage.py — Distill noisy output via Codex. Pipe a big log, test run, or stack
trace in; get back only the signal. The blob is handed to Codex (written to a
temp file so it never goes through argv and never enters Claude's context), and
only Codex's concise summary reaches stdout.

Usage:
    triage.py --focus "what to extract" [--input file]      # or pipe via stdin
    some_command 2>&1 | triage.py --focus "test failures and their root cause"

Examples:
    pytest -v 2>&1 | triage.py --focus "which tests failed and why"
    triage.py --input build.log --focus "the first compiler error"
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

DEFAULT_TIMEOUT = 300


def run_codex(prompt: str, cwd: str | None = None, timeout: int = DEFAULT_TIMEOUT,
              sandbox: str = "workspace-write", model: str | None = None) -> str:
    """Invoke `codex exec` with the safe-default sandbox. Returns its final message."""
    cmd = ["codex", "exec", "--skip-git-repo-check", "--sandbox", sandbox]
    if model:
        cmd += ["--model", model]
    cmd += [prompt]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd,
                          timeout=timeout, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise RuntimeError(f"codex exit {proc.returncode}: {proc.stderr[:500]}")
    return proc.stdout.strip()


def main() -> int:
    ap = argparse.ArgumentParser(description="Distill noisy output via Codex")
    ap.add_argument("--focus", required=True,
                    help="What to extract (e.g. 'failing tests and root cause')")
    ap.add_argument("--input", default=None,
                    help="File to read; if omitted, reads stdin")
    ap.add_argument("--model", default=None, help="Override Codex model")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = ap.parse_args()

    if args.input:
        try:
            blob = Path(args.input).read_text(errors="replace")
        except OSError as e:
            print(f"ERROR: cannot read input: {e}", file=sys.stderr)
            return 1
    else:
        blob = sys.stdin.read()

    if not blob.strip():
        print("ERROR: no input to triage (empty stdin/file)", file=sys.stderr)
        return 1

    # Write the blob to a temp file so it goes via disk, not argv (avoids ARG_MAX
    # and keeps the raw bytes out of Claude's context).
    with tempfile.TemporaryDirectory(prefix="triage_") as td:
        blob_path = Path(td) / "output.log"
        blob_path.write_text(blob)
        prompt = (
            f"Read the file {blob_path.name}. It contains noisy program output "
            f"(logs, test results, or a stack trace). Extract only the signal, "
            f"focused on: {args.focus}\n\n"
            f"Report the few relevant lines and a one-line diagnosis. Be concise; "
            f"do not echo the whole file."
        )
        try:
            summary = run_codex(prompt, cwd=td, timeout=args.timeout, model=args.model)
        except subprocess.TimeoutExpired:
            print("ERROR: Codex timed out", file=sys.stderr)
            return 2
        except (RuntimeError, FileNotFoundError) as e:
            print(f"ERROR: {e}", file=sys.stderr)
            print("Check that 'codex' is in PATH and authenticated (codex login).",
                  file=sys.stderr)
            return 1

    # stdout = only the distilled summary
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
