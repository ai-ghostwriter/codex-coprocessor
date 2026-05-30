# Codex Co-Processor 🧠⚡

> A [Claude Code](https://docs.claude.com/en/docs/claude-code) **plugin** (and
> marketplace) that uses the **Codex CLI** as a co-processor — so token-heavy work
> happens in Codex and only the distilled result reaches Claude.

*[🇮🇹 Versione italiana](README.it.md)*

**The principle:** Claude's expensive resource is its *context window*. Codex
(gpt-5.5, ChatGPT Plus, no API billing) is cheap compute. Every tool here enforces
one discipline:

> **Raw bytes go to Codex. Only the distilled result returns to Claude.**

This keeps sessions long and cheap. Where
[`delegate-to-codex`](https://github.com/ai-ghostwriter/delegate-to-codex) says
"you *can* offload," this suite makes the saving **systematic** for the three
highest-leverage cases.

## The three skills

| Skill | Use it when… | Returns |
|-------|--------------|---------|
| **[codex-recon](skills/codex-recon/)** | you'd read a big file / search a big codebase / fetch web pages just to answer a narrow question | only the distilled answer (raw content never enters Claude's context) |
| **[codex-fanout](skills/codex-fanout/)** | you have N independent token-heavy tasks (process N files, generate N variants) | compact collected results for Claude to merge — run in parallel |
| **[codex-triage](skills/codex-triage/)** | a command produced a huge/noisy log, test run, or stack trace and you need only the signal | the relevant lines + a one-line diagnosis |

Each skill is **self-contained**: its script inlines its own `codex exec` call, so
you can install the whole plugin or symlink just one skill.

## Install as a plugin (recommended)

This repo is both a Claude Code **plugin** and a **marketplace**. The marketplace
also lists the sibling plugins `delegate-to-codex` and `consilium`.

```text
# in Claude Code:
/plugin marketplace add ai-ghostwriter/codex-coprocessor
/plugin install codex-coprocessor@codex-coprocessor
# optional siblings from the same marketplace:
/plugin install delegate-to-codex@codex-coprocessor
/plugin install consilium@codex-coprocessor
```

## Quick start (standalone scripts)

```bash
# Recon: answer a question about a big codebase without reading it into Claude
python skills/codex-recon/scripts/recon.py "What does AuthService.refresh() do?" src/auth/

# Fanout: run N independent tasks in parallel, collect compact results
python skills/codex-fanout/scripts/fanout.py --tasks tasks.json --max-parallel 4 -C /path/to/repo

# Triage: distill a noisy test run down to the signal
pytest -v 2>&1 | python skills/codex-triage/scripts/triage.py --focus "which tests failed and why"
```

All three run Codex with the safe `--sandbox workspace-write` default.

## Requirements

- Python 3.9+ (standard library only — no pip dependencies)
- [`codex`](https://github.com/openai/codex) CLI in PATH, authenticated (`codex login`)

## Manual install (single skill, no plugin)

Claude Code also discovers loose skills in `~/.claude/skills/`. To use just one:

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/dev/codex-coprocessor
ln -s ~/dev/codex-coprocessor/skills/codex-recon ~/.claude/skills/codex-recon
```

Or the whole set:

```bash
for s in codex-recon codex-fanout codex-triage; do
  ln -s ~/dev/codex-coprocessor/skills/$s ~/.claude/skills/$s
done
```

## Testing

```bash
for s in codex-recon codex-fanout codex-triage; do bash skills/$s/scripts/test_smoke.sh; done
```

Each prints `ALL TESTS PASSED`. The tests stub the `codex` binary — fully offline,
no tokens spent. CI runs all three on every push
([`.github/workflows/test.yml`](.github/workflows/test.yml)).

## Design

See [`docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md`](docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md).

## License

[MIT](LICENSE)
