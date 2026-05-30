#!/usr/bin/env python3
"""
recon.py — Context Firewall. Delegate big reads/searches/fetches to Codex and get
back only a distilled answer, so the raw bytes never enter Claude's context.

The script passes *paths/URLs* to Codex; it never reads the content itself. That
is the firewall: large files, search hits and web pages are processed by Codex,
and only its concise answer reaches the caller on stdout.

Usage:
    recon.py "QUESTION" [targets...] [--mode read|search|web]
             [--pattern P] [-C dir] [--model M] [--timeout S]

Examples:
    recon.py "What does AuthService.refresh() do and who calls it?" src/auth/
    recon.py "Where is the rate limit configured?" src/ --mode search --pattern "rate.?limit"
    recon.py "What pricing tiers does this page list?" https://example.com/pricing --mode web
"""
from __future__ import annotations

import argparse
import subprocess
import sys

DEFAULT_TIMEOUT = 600


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


def build_prompt(question: str, targets: list[str], mode: str,
                 pattern: str | None) -> str:
    concise = ("Answer concisely and only with what is relevant. Do NOT dump file "
               "contents or transcripts; report just the answer and minimal "
               "supporting detail.")
    if mode == "search":
        what = pattern or question
        scope = " ".join(targets) if targets else "the current directory"
        return (f"Search {scope} for: {what}\n"
                f"Then answer this question based on what you find:\n{question}\n\n"
                f"{concise}")
    if mode == "web":
        urls = "\n".join(targets)
        return (f"Open these URLs and read their content:\n{urls}\n\n"
                f"Answer this question based on what you read:\n{question}\n\n"
                f"{concise}")
    # read (default)
    files = "\n".join(targets) if targets else "the relevant files in the current directory"
    return (f"Read these files/directories:\n{files}\n\n"
            f"Answer this question:\n{question}\n\n{concise}")


def main() -> int:
    ap = argparse.ArgumentParser(description="Context Firewall: distill big reads via Codex")
    ap.add_argument("question", help="The question Codex should answer")
    ap.add_argument("targets", nargs="*", help="Paths, globs, or URLs to process")
    ap.add_argument("--mode", choices=["read", "search", "web"], default="read")
    ap.add_argument("--pattern", default=None, help="Search pattern (search mode)")
    ap.add_argument("-C", "--cwd", default=None, help="Working directory for Codex")
    ap.add_argument("--model", default=None, help="Override Codex model")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    args = ap.parse_args()

    prompt = build_prompt(args.question, args.targets, args.mode, args.pattern)
    try:
        answer = run_codex(prompt, cwd=args.cwd, timeout=args.timeout, model=args.model)
    except subprocess.TimeoutExpired:
        print("ERROR: Codex timed out", file=sys.stderr)
        return 2
    except (RuntimeError, FileNotFoundError) as e:
        print(f"ERROR: {e}", file=sys.stderr)
        print("Check that 'codex' is in PATH and authenticated (codex login).",
              file=sys.stderr)
        return 1
    # stdout = only the distilled answer (the firewall output)
    print(answer)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
