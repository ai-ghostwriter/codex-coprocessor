---
name: codex-recon
description: Use when you need to read a large file, search or analyze a big codebase, or fetch and extract from web pages, and you want to keep Claude's context small. Delegates the heavy reading to the Codex CLI and returns only a distilled answer — the raw bytes never enter Claude's context. Use when about to read/grep something large just to answer a narrow question, or when context is filling up.
---

# codex-recon — Context Firewall

Delegate big reads, searches and web fetches to the [Codex CLI](https://github.com/openai/codex)
and get back **only a distilled answer**. The raw content is processed by Codex,
so it never enters Claude's context window. This is the systematic version of
"don't read the whole file just to answer one question."

## When to use

- About to `Read`/`Grep` a large file or many files just to answer a narrow question
- Analyzing a big codebase that would blow the context budget
- Extracting a few facts from one or more web pages
- Context is filling up and the remaining work is mostly *reading*

**When NOT to use:** small files you need verbatim, or work that needs Claude's
judgment on the raw content itself.

## How it works

The script passes **paths/URLs** to Codex — it never reads the content itself.
Codex reads/searches/fetches and answers concisely. Only that answer reaches
stdout. That is the firewall.

```bash
# Read mode (default): answer a question using files/dirs
python scripts/recon.py "What does AuthService.refresh() do and who calls it?" src/auth/

# Search mode: grep-then-answer across a tree
python scripts/recon.py "Where is the rate limit configured?" src/ \
    --mode search --pattern "rate.?limit"

# Web mode: fetch URLs and extract
python scripts/recon.py "What pricing tiers does this list?" \
    https://example.com/pricing --mode web
```

Flags: `--mode read|search|web`, `--pattern P` (search), `-C dir`, `--model M`,
`--timeout S`. Codex runs with the safe `--sandbox workspace-write` default.

## Test

```bash
bash scripts/test_smoke.sh   # offline, stubbed codex, no tokens; asserts the firewall holds
```

## Requirements

- Python 3.9+ (standard library only)
- [`codex`](https://github.com/openai/codex) CLI in PATH, authenticated (`codex login`)
