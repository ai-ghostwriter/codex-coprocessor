---
name: codex-triage
description: Use when a command produced a large or noisy output — a long test run, a verbose build log, a big stack trace — and you only need the signal (what failed and why). Pipes the blob to the Codex CLI, which extracts the relevant lines and a one-line diagnosis, so the raw output never enters Claude's context. Use instead of reading thousands of log lines yourself.
---

# codex-triage — Output distiller

Pipe a noisy blob (test output, build log, stack trace) to the
[Codex CLI](https://github.com/openai/codex) and get back only the signal. The
blob is handed to Codex via a temp file, so the raw output never enters Claude's
context — Claude sees only the concise summary.

## When to use

- A long/verbose command output where you only need *what failed and why*
- Test runs, build logs, stack traces, linter dumps
- Any output too big to be worth reading line by line

**When NOT to use:** short output you can read directly, or when you need the
exact verbatim text for a precise edit.

## How it works

```bash
# Pipe via stdin
pytest -v 2>&1 | python scripts/triage.py --focus "which tests failed and why"

npm run build 2>&1 | python scripts/triage.py --focus "the first compiler error"

# Or read a file
python scripts/triage.py --input build.log --focus "the root cause of the failure"
```

The blob (stdin or `--input`) is written to a temp file; Codex reads it and
reports only the relevant lines plus a one-line diagnosis on stdout.

Flags: `--focus "..."` (required), `--input FILE`, `--model M`, `--timeout S`.
Codex runs with the safe `--sandbox workspace-write` default.

## Test

```bash
bash scripts/test_smoke.sh   # offline, stubbed codex, no tokens; asserts noise never leaks
```

## Requirements

- Python 3.9+ (standard library only)
- [`codex`](https://github.com/openai/codex) CLI in PATH, authenticated (`codex login`)
