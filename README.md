# Codex Co-Processor

*[Versione italiana](README.it.md)*

## Table of Contents

- [What It Includes](#what-it-includes)
- [Requirements](#requirements)
- [Install From The Plugin Marketplace](#install-from-the-plugin-marketplace)
- [Manual Install](#manual-install)
- [How To Use It In Prompts](#how-to-use-it-in-prompts)
  - [`/codex-recon` Examples](#codex-recon-examples)
  - [`/codex-fanout` Examples](#codex-fanout-examples)
  - [`/codex-triage` Examples](#codex-triage-examples)
- [Running The Scripts Directly](#running-the-scripts-directly)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing)
- [License](#license)

Codex Co-Processor is a Claude Code plugin for people who use Claude Code and also have the Codex CLI installed.

It solves a simple problem: sometimes Claude would need to read a lot of files, process many similar tasks, or inspect a very long error log. That can fill Claude's chat context with raw text. This plugin lets Claude ask Codex to do that heavy reading first, then bring back only the short useful answer.

You do not need to understand agents, context windows, or automation frameworks to use it. Install the plugin, then type one of its slash commands inside your normal Claude Code chat message.

## What It Includes

The plugin adds three skills:

| Skill | Use it for |
| --- | --- |
| `/codex-recon` | Ask a focused question about large files, folders, or a codebase without pasting everything into Claude. |
| `/codex-fanout` | Run several independent tasks in parallel, such as converting many files or summarizing many documents. |
| `/codex-triage` | Reduce a long terminal output, test log, build log, or stack trace to the important failure and likely cause. |

## Requirements

You need:

- Claude Code installed.
- Codex CLI installed.
- Codex CLI logged in with a ChatGPT account.

To log in to Codex, run this in your terminal:

```bash
codex login
```

If `codex` is not found, install or fix the Codex CLI first, then come back to this plugin.

## Install From The Plugin Marketplace

Type these commands inside the Claude Code chat box, not in your normal terminal:

```text
/plugin marketplace add ai-ghostwriter/codex-coprocessor
/plugin install codex-coprocessor@codex-coprocessor
```

After installation, restart Claude Code or run `/reload-plugins` if Claude Code asks you to reload plugins.

## Manual Install

Use this if you do not want to install through the plugin marketplace.

1. Clone the repository:

```bash
git clone https://github.com/ai-ghostwriter/codex-coprocessor.git ~/codex-coprocessor
```

2. Create your Claude Code skills folder if it does not exist:

```bash
mkdir -p ~/.claude/skills
```

3. Link each skill folder:

```bash
ln -s ~/codex-coprocessor/skills/codex-recon ~/.claude/skills/codex-recon
ln -s ~/codex-coprocessor/skills/codex-fanout ~/.claude/skills/codex-fanout
ln -s ~/codex-coprocessor/skills/codex-triage ~/.claude/skills/codex-triage
```

4. Restart Claude Code or run `/reload-plugins`.

## How To Use It In Prompts

You use a skill by typing its slash command directly inside a normal Claude Code chat message.

For example, do not run `/codex-recon` in the terminal. Type a message like this in Claude Code:

```text
Analyze the whole src folder and tell me where authentication is handled, use /codex-recon
```

### `/codex-recon` Examples

```text
Analyze the whole src folder and tell me where authentication is handled, use /codex-recon
```

```text
Use /codex-recon to inspect README.md and skills/codex-recon/scripts/recon.py, then explain the exact command flags.
```

```text
Use /codex-recon to search this project for where Codex CLI is called and summarize the result.
```

### `/codex-fanout` Examples

```text
Use /codex-fanout to convert every file in ./data to JSON. Each file is independent.
```

```text
Use /codex-fanout to summarize each markdown file in ./docs separately, then give me one combined index.
```

```text
Use /codex-fanout to review each package under ./packages independently and report the main risk in each one.
```

### `/codex-triage` Examples

```text
I pasted a long test failure below. Use /codex-triage to tell me which test failed first and why.
```

```text
Run the build, then use /codex-triage on the output and tell me the first real compiler error.
```

```text
Use /codex-triage to reduce this stack trace to the root cause and the file I should inspect first.
```

## Running The Scripts Directly

The plugin is designed for Claude Code prompts, but each skill also includes a script:

```bash
python3 skills/codex-recon/scripts/recon.py "Where is login handled?" src/
python3 skills/codex-fanout/scripts/fanout.py --tasks tasks.json --max-parallel 4
pytest -v 2>&1 | python3 skills/codex-triage/scripts/triage.py --focus "first failing test"
```

## Troubleshooting

If Claude Code does not recognize the slash commands, restart Claude Code or run `/reload-plugins`.

If Codex fails, run `codex login` in your terminal and make sure `codex` works before using the plugin again.

If marketplace installation fails, check that you typed the commands inside the Claude Code chat box:

```text
/plugin marketplace add ai-ghostwriter/codex-coprocessor
/plugin install codex-coprocessor@codex-coprocessor
```

If manual installation fails, check that the symlinks point to real folders under `~/codex-coprocessor/skills/`.

## Testing

The repository includes offline smoke tests. They use a fake `codex` command, so they do not spend tokens or call the real Codex CLI:

```bash
for s in codex-recon codex-fanout codex-triage; do bash "skills/$s/scripts/test_smoke.sh"; done
```

## License

[MIT](LICENSE)
