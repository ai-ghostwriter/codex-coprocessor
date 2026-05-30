---
name: codex-fanout
description: Use when you have several independent, token-heavy tasks to run (process N files, generate N variants, summarize N documents) and you want them done in parallel without filling Claude's context. Dispatches each task to its own Codex process concurrently and returns only the compact collected results for Claude to merge. Use for batch/bulk work with no shared state between tasks.
---

# codex-fanout — Parallel map-reduce over Codex

Run N independent token-heavy tasks as N concurrent [Codex CLI](https://github.com/openai/codex)
processes, then let Claude merge only the compact results. The per-task work
happens in Codex, so Claude's context stays small.

## When to use

- A batch of *independent* tasks: summarize 30 files, generate 20 variants,
  analyze each module separately
- Work with **no shared state** between items (each task is self-contained)
- You only need Claude to synthesize the collected outputs

**When NOT to use:** tasks that depend on each other's output (sequential), or a
single task (just use `codex-recon` or `delegate-to-codex`).

## How it works

Provide a JSON array of tasks. Each runs in its own `codex exec`; results are
collected, id-ordered, into one compact JSON.

```bash
cat > tasks.json <<'JSON'
[
  {"id": "auth",  "prompt": "Summarize src/auth/ in 5 bullets",   "output_path": "out/auth.md"},
  {"id": "api",   "prompt": "Summarize src/api/ in 5 bullets"},
  {"id": "db",    "prompt": "Summarize src/db/ in 5 bullets"}
]
JSON

python scripts/fanout.py --tasks tasks.json --max-parallel 4 -C /path/to/repo
```

Output: `[{id, result, status, error?}]` written to `--output`
(`fanout_results.json`) and printed to stdout. Tasks with `output_path` also get
their result written there. A failing task is isolated as `status: error`; the
rest still complete.

Flags: `--max-parallel N` (default 4), `-C dir`, `--model M`, `--timeout S`,
`--output FILE`. Codex runs with the safe `--sandbox workspace-write` default.

## Test

```bash
bash scripts/test_smoke.sh   # offline, stubbed codex, no tokens
```

## Requirements

- Python 3.9+ (standard library only)
- [`codex`](https://github.com/openai/codex) CLI in PATH, authenticated (`codex login`)
