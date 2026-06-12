# Codex Co-Processor

*[English version](README.md)*

Codex Co-Processor è un plugin per Claude Code pensato per chi usa Claude Code e ha installato anche la Codex CLI.

Risolve un problema semplice: a volte Claude dovrebbe leggere molti file, processare tanti compiti simili, oppure controllare un log di errore molto lungo. Questo può riempire la chat di Claude con testo grezzo. Questo plugin permette a Claude di chiedere prima a Codex di fare la lettura pesante, e poi riportare in chat solo la risposta breve e utile.

Non devi conoscere agenti, finestre di contesto o framework di automazione per usarlo. Installi il plugin, poi scrivi uno dei suoi comandi slash dentro un normale messaggio nella chat di Claude Code.

## Cosa Include

Il plugin aggiunge tre skill:

| Skill | A cosa serve |
| --- | --- |
| `/codex-recon` | Fare una domanda mirata su file grandi, cartelle o una codebase senza incollare tutto dentro Claude. |
| `/codex-fanout` | Eseguire più compiti indipendenti in parallelo, per esempio convertire molti file o riassumere molti documenti. |
| `/codex-triage` | Ridurre un output terminale lungo, un log di test, un log di build o uno stack trace al fallimento importante e alla causa probabile. |

## Requisiti

Ti servono:

- Claude Code installato.
- Codex CLI installata.
- Codex CLI collegata con un account ChatGPT.

Per fare login in Codex, esegui questo nel terminale:

```bash
codex login
```

Se `codex` non viene trovato, installa o sistema prima la Codex CLI, poi torna a questo plugin.

## Installazione Dal Plugin Marketplace

Scrivi questi comandi dentro la chat di Claude Code, non nel terminale normale:

```text
/plugin marketplace add ai-ghostwriter/codex-coprocessor
/plugin install codex-coprocessor@codex-coprocessor
```

Dopo l'installazione, riavvia Claude Code oppure esegui `/reload-plugins` se Claude Code ti chiede di ricaricare i plugin.

## Installazione Manuale

Usa questa strada se non vuoi installare dal plugin marketplace.

1. Clona il repository:

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/codex-coprocessor
```

2. Crea la cartella delle skill di Claude Code se non esiste:

```bash
mkdir -p ~/.claude/skills
```

3. Collega ogni cartella skill:

```bash
ln -s ~/codex-coprocessor/skills/codex-recon ~/.claude/skills/codex-recon
ln -s ~/codex-coprocessor/skills/codex-fanout ~/.claude/skills/codex-fanout
ln -s ~/codex-coprocessor/skills/codex-triage ~/.claude/skills/codex-triage
```

4. Riavvia Claude Code oppure esegui `/reload-plugins`.

## Come Usarlo Nei Prompt

Usi una skill scrivendo il suo comando slash direttamente dentro un normale messaggio nella chat di Claude Code.

Per esempio, non devi eseguire `/codex-recon` nel terminale. Devi scrivere un messaggio così in Claude Code:

```text
Analizza tutta la cartella src e dimmi dove viene gestita l autenticazione, usa /codex-recon
```

### Esempi Per `/codex-recon`

```text
Analizza tutta la cartella src e dimmi dove viene gestita l autenticazione, usa /codex-recon
```

```text
Usa /codex-recon per controllare README.md e skills/codex-recon/scripts/recon.py, poi spiegami i flag esatti del comando.
```

```text
Usa /codex-recon per cercare in questo progetto dove viene chiamata la Codex CLI e riassumi il risultato.
```

### Esempi Per `/codex-fanout`

```text
Usa /codex-fanout per convertire ogni file in ./data in JSON. Ogni file è indipendente.
```

```text
Usa /codex-fanout per riassumere separatamente ogni file markdown in ./docs, poi dammi un indice unico.
```

```text
Usa /codex-fanout per revisionare ogni package dentro ./packages in modo indipendente e riportare il rischio principale di ciascuno.
```

### Esempi Per `/codex-triage`

```text
Ho incollato sotto un errore di test molto lungo. Usa /codex-triage per dirmi quale test fallisce per primo e perché.
```

```text
Esegui la build, poi usa /codex-triage sull output e dimmi il primo vero errore di compilazione.
```

```text
Usa /codex-triage per ridurre questo stack trace alla causa principale e al file che devo controllare per primo.
```

## Eseguire Gli Script Direttamente

Il plugin è pensato per i prompt in Claude Code, ma ogni skill include anche uno script:

```bash
python3 skills/codex-recon/scripts/recon.py "Dove viene gestito il login?" src/
python3 skills/codex-fanout/scripts/fanout.py --tasks tasks.json --max-parallel 4
pytest -v 2>&1 | python3 skills/codex-triage/scripts/triage.py --focus "primo test fallito"
```

## Risoluzione Problemi

Se Claude Code non riconosce i comandi slash, riavvia Claude Code oppure esegui `/reload-plugins`.

Se Codex fallisce, esegui `codex login` nel terminale e assicurati che `codex` funzioni prima di usare di nuovo il plugin.

Se l'installazione dal marketplace fallisce, controlla di aver scritto i comandi dentro la chat di Claude Code:

```text
/plugin marketplace add ai-ghostwriter/codex-coprocessor
/plugin install codex-coprocessor@codex-coprocessor
```

Se l'installazione manuale fallisce, controlla che i symlink puntino a cartelle reali dentro `~/codex-coprocessor/skills/`.

## Test

Il repository include smoke test offline. Usano un comando `codex` finto, quindi non consumano token e non chiamano la vera Codex CLI:

```bash
for s in codex-recon codex-fanout codex-triage; do bash "skills/$s/scripts/test_smoke.sh"; done
```

## Licenza

[MIT](LICENSE)
