# Codex Co-Processor 🧠⚡

> A suite of [Claude Code](https://docs.claude.com/en/docs/claude-code) skills
> that use the **Codex CLI** as a co-processor — so token-heavy work happens in
> Codex and only the distilled result reaches Claude.

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
| **[codex-recon](codex-recon/)** | you'd read a big file / search a big codebase / fetch web pages just to answer a narrow question | only the distilled answer (raw content never enters Claude's context) |
| **[codex-fanout](codex-fanout/)** | you have N independent token-heavy tasks (process N files, generate N variants) | compact collected results for Claude to merge — run in parallel |
| **[codex-triage](codex-triage/)** | a command produced a huge/noisy log, test run, or stack trace and you need only the signal | the relevant lines + a one-line diagnosis |

Each skill is **self-contained**: its script inlines its own `codex exec` call, so
you can install the whole suite or just one skill.

## Quick start

```bash
# Recon: answer a question about a big codebase without reading it into Claude
python codex-recon/scripts/recon.py "What does AuthService.refresh() do?" src/auth/

# Fanout: run N independent tasks in parallel, collect compact results
python codex-fanout/scripts/fanout.py --tasks tasks.json --max-parallel 4 -C /path/to/repo

# Triage: distill a noisy test run down to the signal
pytest -v 2>&1 | python codex-triage/scripts/triage.py --focus "which tests failed and why"
```

All three run Codex with the safe `--sandbox workspace-write` default.

## Requirements

- Python 3.9+ (standard library only — no pip dependencies)
- [`codex`](https://github.com/openai/codex) CLI in PATH, authenticated (`codex login`)

## Installing as Claude Code skills

Claude Code discovers skills in your central skills directory, `~/.claude/skills/`.
The folder name there must match each skill's name.

### Option A — Whole suite via symlinks

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/dev/codex-coprocessor
for s in codex-recon codex-fanout codex-triage; do
  ln -s ~/dev/codex-coprocessor/$s ~/.claude/skills/$s
done
```

### Option B — Just one skill

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/dev/codex-coprocessor
ln -s ~/dev/codex-coprocessor/codex-recon ~/.claude/skills/codex-recon
```

Edit in `~/dev/codex-coprocessor`, `git pull` there, and the symlinks keep
`~/.claude/skills/` in sync.

## Testing

```bash
for s in codex-recon codex-fanout codex-triage; do bash $s/scripts/test_smoke.sh; done
```

Each prints `ALL TESTS PASSED`. The tests stub the `codex` binary — fully offline,
no tokens spent. CI runs all three on every push
([`.github/workflows/test.yml`](.github/workflows/test.yml)).

## Design

See [`docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md`](docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md).

## License

[MIT](LICENSE)
