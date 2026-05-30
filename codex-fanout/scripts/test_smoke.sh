#!/usr/bin/env bash
#
# test_smoke.sh — Validate fanout.py WITHOUT calling the real Codex.
#
# Stubs `codex` so that a normal prompt returns a canned result, but a prompt
# containing the token FAILME exits non-zero. Verifies: all tasks complete,
# id order is preserved, a failing task is isolated as status=error while the
# others stay ok, and per-task output_path is written.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/fanout.py"
SANDBOX="$(mktemp -d)"
BIN="$SANDBOX/bin"; mkdir -p "$BIN"
RUN="$SANDBOX/run"; mkdir -p "$RUN"
trap 'rm -rf "$SANDBOX"' EXIT

# Stub codex: echo a canned result; fail if the prompt contains FAILME.
cat > "$BIN/codex" <<'STUB'
#!/usr/bin/env bash
args="$*"
if echo "$args" | grep -q "FAILME"; then
  echo "kaboom" >&2
  exit 1
fi
echo "RESULT for task"
STUB
chmod +x "$BIN/codex"
export PATH="$BIN:$PATH"

# Three tasks; the middle one is designed to fail. One has an output_path.
cat > "$RUN/tasks.json" <<JSON
[
  {"id": "a", "prompt": "do thing A", "output_path": "out/a.txt"},
  {"id": "b", "prompt": "do thing B FAILME"},
  {"id": "c", "prompt": "do thing C"}
]
JSON

fail=0
echo "=== run fanout (max-parallel 2) ==="
python3 "$SCRIPT" --tasks "$RUN/tasks.json" --max-parallel 2 \
        -C "$RUN" --output results.json >"$RUN/stdout.txt" 2>"$RUN/stderr.txt"
cat "$RUN/stdout.txt"
echo "--- stderr ---"; cat "$RUN/stderr.txt"

echo
echo "=== ASSERTIONS ==="
python3 - "$RUN/results.json" <<'PY'
import json, sys
r = json.load(open(sys.argv[1]))
ids = [x["id"] for x in r]
assert ids == ["a", "b", "c"], f"order not preserved: {ids}"
st = {x["id"]: x["status"] for x in r}
assert st["a"] == "ok" and st["c"] == "ok", f"good tasks not ok: {st}"
assert st["b"] == "error", f"failing task not isolated: {st}"
assert "kaboom" in (next(x for x in r if x['id']=='b').get('error') or ''), "error not captured"
assert "RESULT for task" in next(x for x in r if x['id']=='a')["result"], "good result missing"
print("OK  3 tasks, order preserved, failure isolated, good tasks ok")
PY
[ $? -eq 0 ] || fail=1

# output_path written for task a
if [ -f "$RUN/out/a.txt" ] && grep -q "RESULT for task" "$RUN/out/a.txt"; then
  echo "OK  per-task output_path written"
else
  echo "FAIL output_path not written"; fail=1
fi

# aggregate present on stdout
if grep -q '"status": "error"' "$RUN/stdout.txt" && grep -q '"id": "c"' "$RUN/stdout.txt"; then
  echo "OK  aggregate JSON printed to stdout"
else
  echo "FAIL aggregate not on stdout"; fail=1
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "########## ALL TESTS PASSED ##########"
else
  echo "########## THERE ARE FAILURES (see above) ##########"; exit 1
fi
