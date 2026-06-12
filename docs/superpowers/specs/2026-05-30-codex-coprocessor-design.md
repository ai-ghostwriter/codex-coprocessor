# codex-coprocessor — Design Spec

**Date:** 2026-05-30
**Status:** Approved

## Principle

Claude's expensive resource is its **context window**. The Codex CLI can do the
large reading or batch work in a separate process. The whole suite enforces one
discipline: **raw bytes go to Codex; only the distilled result returns to
Claude.** This saves tokens and extends sessions.

`delegate-to-codex` already says "you *can* offload." This suite makes the saving
**systematic**: three focused tools for the three highest-leverage cases.

## Architecture

A single monorepo, `codex-coprocessor`, with three **self-contained** skill
folders. Each folder inlines its own ~25-line `codex exec` call so it can be
symlinked into `~/.claude/skills/` on its own, with no shared dependency. (A
shared `lib/` was rejected because it would break single-skill installs; the only
duplicated surface is the subprocess wrapper.)

Every Codex invocation uses the **safe default**: `--sandbox workspace-write`,
stdin closed (`stdin=DEVNULL`), final message captured. No dangerous flags by
default.

```
codex-coprocessor/
├── README.md / README.it.md
├── LICENSE (MIT) / .gitignore
├── .github/workflows/test.yml      # runs all three smoke tests
├── docs/superpowers/specs/         # this spec
├── .claude-plugin/{plugin.json, marketplace.json}
└── skills/
    ├── codex-recon/{SKILL.md, scripts/recon.py, scripts/test_smoke.sh}
    ├── codex-fanout/{SKILL.md, scripts/fanout.py, scripts/test_smoke.sh}
    └── codex-triage/{SKILL.md, scripts/triage.py, scripts/test_smoke.sh}
```

## Components

### codex-recon — Context Firewall
- **Interface:** `recon.py "QUESTION" [targets...] [--mode read|search|web]
  [--pattern P] [-C dir] [--model M] [--timeout S]`
- **Behavior:** Codex reads the targets / searches / fetches URLs and answers the
  question concisely. The script passes *paths* to Codex — raw content never
  passes through the script, so it never enters Claude's context. stdout = only
  Codex's distilled answer.
- **Firewall test:** a sentinel string inside a target file must NOT appear in
  stdout; the distilled answer must.

### codex-fanout — parallel map-reduce
- **Interface:** `fanout.py --tasks tasks.json [--max-parallel 4] [-C dir]
  [--model M] [--timeout S] [--output fanout_results.json]`
- **Input:** `tasks.json = [{"id": str, "prompt": str, "output_path"?: str}]`
- **Behavior:** runs N `codex exec` concurrently (thread pool, I/O bound),
  collects each final message into `[{id, result, status, error?}]`, preserving
  id order. Writes aggregate to `--output` and prints it to stdout. If a task has
  `output_path`, its result is also written there.
- **Test:** 3 tasks → 3 `ok`; a failing task → isolated `status: error`, others
  still `ok`; results keyed/ordered by id.

### codex-triage — output distiller
- **Interface:** `triage.py [--input file | stdin] --focus "what to extract"
  [--model M] [--timeout S]`
- **Behavior:** reads a noisy blob (logs/test output/stack traces), writes it to a
  temp file, tells Codex to read that file and extract the signal focused on
  `--focus`. Passing via temp file (not argv) avoids ARG_MAX and reinforces the
  firewall. stdout = only the concise summary.
- **Test:** canned noisy log in → concise summary out; the noisy sentinel lines
  must NOT appear in stdout.

## Testing

Each skill ships `scripts/test_smoke.sh` that stubs the `codex` binary with a fake
executable returning canned output (zero tokens, fully offline), mirroring the
`consilium` approach. CI runs all three on every push.

## Out of scope (YAGNI)

- `consilium` and `delegate-to-codex` stay as separate repos.
- Auto-offload hooks, model auto-selection, retries beyond a single failure path.
