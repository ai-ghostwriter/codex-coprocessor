# Codex Co-Processor 🧠⚡

> Una suite di skill per [Claude Code](https://docs.claude.com/en/docs/claude-code)
> che usano il **Codex CLI** come co-processore — così il lavoro pesante in token
> avviene in Codex e a Claude torna solo il risultato distillato.

*[🇬🇧 English version](README.md)*

**Il principio:** la risorsa costosa di Claude è la *finestra di contesto*. Codex
(gpt-5.5, ChatGPT Plus, niente API billing) è compute a basso costo. Ogni
strumento qui impone una disciplina sola:

> **I byte grezzi vanno a Codex. A Claude torna solo il distillato.**

Così le sessioni restano lunghe ed economiche. Dove
[`delegate-to-codex`](https://github.com/ai-ghostwriter/delegate-to-codex) dice
"*puoi* delegare", questa suite rende il risparmio **sistematico** per i tre casi
a più alta leva.

## Le tre skill

| Skill | Usala quando… | Restituisce |
|-------|---------------|-------------|
| **[codex-recon](codex-recon/)** | leggeresti un file enorme / cercheresti in una codebase grande / fetch di pagine web solo per rispondere a una domanda mirata | solo la risposta distillata (il contenuto grezzo non entra mai nel contesto di Claude) |
| **[codex-fanout](codex-fanout/)** | hai N task indipendenti e pesanti (processa N file, genera N varianti) | i risultati compatti raccolti, da fondere — eseguiti in parallelo |
| **[codex-triage](codex-triage/)** | un comando ha prodotto un log/test/stacktrace enorme e ti serve solo il segnale | le righe rilevanti + una diagnosi in una riga |

Ogni skill è **auto-contenuta**: il suo script inlinea la propria chiamata
`codex exec`, così puoi installare l'intera suite o una sola skill.

## Avvio rapido

```bash
# Recon: rispondi su una codebase grande senza leggerla dentro Claude
python codex-recon/scripts/recon.py "Cosa fa AuthService.refresh()?" src/auth/

# Fanout: N task indipendenti in parallelo, risultati compatti
python codex-fanout/scripts/fanout.py --tasks tasks.json --max-parallel 4 -C /path/to/repo

# Triage: distilla un test run rumoroso fino al segnale
pytest -v 2>&1 | python codex-triage/scripts/triage.py --focus "quali test falliscono e perché"
```

Tutte e tre eseguono Codex col default sicuro `--sandbox workspace-write`.

## Requisiti

- Python 3.9+ (solo libreria standard — nessuna dipendenza pip)
- CLI [`codex`](https://github.com/openai/codex) in PATH, autenticato (`codex login`)

## Installazione come skill di Claude Code

Claude Code scopre le skill nella directory centrale `~/.claude/skills/`. Lì il
nome della cartella deve combaciare col nome di ogni skill.

### Opzione A — Intera suite via symlink

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/dev/codex-coprocessor
for s in codex-recon codex-fanout codex-triage; do
  ln -s ~/dev/codex-coprocessor/$s ~/.claude/skills/$s
done
```

### Opzione B — Una sola skill

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/dev/codex-coprocessor
ln -s ~/dev/codex-coprocessor/codex-recon ~/.claude/skills/codex-recon
```

Modifichi in `~/dev/codex-coprocessor`, fai `git pull` lì, e i symlink mantengono
`~/.claude/skills/` allineata.

> 💡 È la stessa convenzione di `~/.claude/skills/` su questa macchina: solo
> symlink che puntano alle skill mantenute altrove.

## Test

```bash
for s in codex-recon codex-fanout codex-triage; do bash $s/scripts/test_smoke.sh; done
```

Ognuno stampa `ALL TESTS PASSED`. I test stubbano il binario `codex` — del tutto
offline, nessun token speso. La CI li esegue tutti e tre a ogni push.

## Design

Vedi [`docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md`](docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md).

## Licenza

[MIT](LICENSE)
