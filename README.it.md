# Codex Co-Processor 🧠⚡

> Un **plugin** (e marketplace) per [Claude Code](https://docs.claude.com/en/docs/claude-code)
> che usa il **Codex CLI** come co-processore — così il lavoro pesante in token
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
| **[codex-recon](skills/codex-recon/)** | leggeresti un file enorme / cercheresti in una codebase grande / fetch di pagine web solo per rispondere a una domanda mirata | solo la risposta distillata (il contenuto grezzo non entra mai nel contesto di Claude) |
| **[codex-fanout](skills/codex-fanout/)** | hai N task indipendenti e pesanti (processa N file, genera N varianti) | i risultati compatti raccolti, da fondere — eseguiti in parallelo |
| **[codex-triage](skills/codex-triage/)** | un comando ha prodotto un log/test/stacktrace enorme e ti serve solo il segnale | le righe rilevanti + una diagnosi in una riga |

Ogni skill è **auto-contenuta**: il suo script inlinea la propria chiamata
`codex exec`, così puoi installare l'intero plugin o symlinkare una sola skill.

## Installazione come plugin (consigliata)

Questo repo è insieme un **plugin** e una **marketplace** per Claude Code. La
marketplace elenca anche i plugin gemelli `delegate-to-codex` e `consilium`.

```text
# dentro Claude Code:
/plugin marketplace add ai-ghostwriter/codex-coprocessor
/plugin install codex-coprocessor@codex-coprocessor
# gemelli opzionali dalla stessa marketplace:
/plugin install delegate-to-codex@codex-coprocessor
/plugin install consilium@codex-coprocessor
```

## Avvio rapido (script standalone)

```bash
# Recon: rispondi su una codebase grande senza leggerla dentro Claude
python skills/codex-recon/scripts/recon.py "Cosa fa AuthService.refresh()?" src/auth/

# Fanout: N task indipendenti in parallelo, risultati compatti
python skills/codex-fanout/scripts/fanout.py --tasks tasks.json --max-parallel 4 -C /path/to/repo

# Triage: distilla un test run rumoroso fino al segnale
pytest -v 2>&1 | python skills/codex-triage/scripts/triage.py --focus "quali test falliscono e perché"
```

Tutte e tre eseguono Codex col default sicuro `--sandbox workspace-write`.

## Requisiti

- Python 3.9+ (solo libreria standard — nessuna dipendenza pip)
- CLI [`codex`](https://github.com/openai/codex) in PATH, autenticato (`codex login`)

## Installazione manuale (singola skill, senza plugin)

Claude Code scopre anche le skill sciolte in `~/.claude/skills/`. Per usarne una:

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/dev/codex-coprocessor
ln -s ~/dev/codex-coprocessor/skills/codex-recon ~/.claude/skills/codex-recon
```

Oppure tutte:

```bash
for s in codex-recon codex-fanout codex-triage; do
  ln -s ~/dev/codex-coprocessor/skills/$s ~/.claude/skills/$s
done
```

## Test

```bash
for s in codex-recon codex-fanout codex-triage; do bash skills/$s/scripts/test_smoke.sh; done
```

Ognuno stampa `ALL TESTS PASSED`. I test stubbano il binario `codex` — del tutto
offline, nessun token speso. La CI li esegue tutti e tre a ogni push.

## Design

Vedi [`docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md`](docs/superpowers/specs/2026-05-30-codex-coprocessor-design.md).

## Licenza

[MIT](LICENSE)
