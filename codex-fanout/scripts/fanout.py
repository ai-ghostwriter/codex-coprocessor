#!/usr/bin/env python3
"""
fanout.py — Parallel map-reduce over Codex. Run N independent token-heavy tasks as
N concurrent `codex exec` processes, then collect only the compact results, so
Claude does the merge instead of doing all the work in-context.

Input: a JSON file of tasks:
    [
      {"id": "chap1", "prompt": "Summarize file A ...", "output_path": "out/a.md"},
      {"id": "chap2", "prompt": "Summarize file B ..."}
    ]

Output: an aggregate JSON [{id, result, status, error?}] written to --output and
printed to stdout. If a task has "output_path", its result is also written there.

Usage:
    fanout.py --tasks tasks.json [--max-parallel 4] [-C dir]
              [--model M] [--timeout S] [--output fanout_results.json]
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

DEFAULT_TIMEOUT = 600


def run_codex(prompt: str, cwd: str | None = None, timeout: int = DEFAULT_TIMEOUT,
              sandbox: str = "workspace-write", model: str | None = None) -> str:
    """Invoke `codex exec` with the safe-default sandbox. Returns its final message."""
    cmd = ["codex", "exec", "--skip-git-repo-check", "--sandbox", sandbox]
    if model:
        cmd += ["--model", model]
    cmd += [prompt]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd,
                          timeout=timeout, stdin=subprocess.DEVNULL)
    if proc.returncode != 0:
        raise RuntimeError(f"codex exit {proc.returncode}: {proc.stderr[:500]}")
    return proc.stdout.strip()


def run_task(task: dict, cwd: str | None, timeout: int, model: str | None) -> dict:
    """Run one task. Never raises: failures are captured as status=error."""
    tid = task.get("id", "?")
    prompt = task.get("prompt", "")
    if not prompt:
        return {"id": tid, "result": "", "status": "error", "error": "empty prompt"}
    try:
        result = run_codex(prompt, cwd=cwd, timeout=timeout, model=model)
    except subprocess.TimeoutExpired:
        return {"id": tid, "result": "", "status": "error", "error": "timeout"}
    except (RuntimeError, FileNotFoundError) as e:
        return {"id": tid, "result": "", "status": "error", "error": str(e)[:300]}
    out = {"id": tid, "result": result, "status": "ok"}
    if task.get("output_path"):
        try:
            p = Path(task["output_path"])
            if cwd and not p.is_absolute():
                p = Path(cwd) / p
            p.parent.mkdir(parents=True, exist_ok=True)
            p.write_text(result)
            out["written_to"] = str(p)
        except OSError as e:
            out["write_error"] = str(e)[:200]
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="Parallel map-reduce over Codex")
    ap.add_argument("--tasks", required=True, help="JSON file: [{id, prompt, output_path?}]")
    ap.add_argument("--max-parallel", type=int, default=4)
    ap.add_argument("-C", "--cwd", default=None, help="Working directory for Codex")
    ap.add_argument("--model", default=None, help="Override Codex model")
    ap.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT)
    ap.add_argument("--output", default="fanout_results.json")
    args = ap.parse_args()

    try:
        tasks = json.loads(Path(args.tasks).read_text())
    except (OSError, json.JSONDecodeError) as e:
        print(f"ERROR: cannot read tasks file: {e}", file=sys.stderr)
        return 1
    if not isinstance(tasks, list) or not tasks:
        print("ERROR: tasks file must be a non-empty JSON array", file=sys.stderr)
        return 1

    # Preserve input order by id while running concurrently.
    order = [t.get("id", str(i)) for i, t in enumerate(tasks)]
    results: dict[str, dict] = {}
    with ThreadPoolExecutor(max_workers=max(1, args.max_parallel)) as ex:
        futures = {ex.submit(run_task, t, args.cwd, args.timeout, args.model):
                   t.get("id", str(i)) for i, t in enumerate(tasks)}
        for fut in futures:
            r = fut.result()
            results[r["id"]] = r

    ordered = [results[tid] for tid in order if tid in results]
    aggregate = json.dumps(ordered, indent=2, ensure_ascii=False)

    out_path = Path(args.output)
    if args.cwd and not out_path.is_absolute():
        out_path = Path(args.cwd) / out_path
    try:
        out_path.write_text(aggregate)
    except OSError as e:
        print(f"WARN: could not write {out_path}: {e}", file=sys.stderr)

    print(aggregate)
    n_err = sum(1 for r in ordered if r["status"] == "error")
    print(f"\n[fanout: {len(ordered)} tasks, {n_err} failed -> {out_path}]",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
