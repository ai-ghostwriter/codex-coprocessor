#!/usr/bin/env bash
#
# test_smoke.sh — Validate triage.py WITHOUT calling the real Codex.
#
# Stubs `codex` to return a canned concise summary. Verifies: a noisy blob piped
# via stdin produces only the summary on stdout, the noisy sentinel lines do NOT
# leak to stdout, the --input file path works, and empty input is rejected.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/triage.py"
SANDBOX="$(mktemp -d)"
BIN="$SANDBOX/bin"; mkdir -p "$BIN"
trap 'rm -rf "$SANDBOX"' EXIT

NOISE="NOISYLINE_SHOULD_NOT_LEAK_0xC0FFEE"

# Stub codex: ignore the file, return a canned concise summary.
cat > "$BIN/codex" <<'STUB'
#!/usr/bin/env bash
echo "SUMMARY: 2 tests failed in test_auth.py; root cause: expired token fixture."
STUB
chmod +x "$BIN/codex"
export PATH="$BIN:$PATH"

# Build a big noisy log.
BIG="$SANDBOX/build.log"
for i in $(seq 1 300); do echo "[$i] $NOISE blah blah"; done > "$BIG"

fail=0
echo "=== TEST 1: stdin pipe -> only the summary ==="
OUT="$(cat "$BIG" | python3 "$SCRIPT" --focus "failing tests and root cause")"
echo "stdout: $OUT"
if echo "$OUT" | grep -q "SUMMARY:"; then
  echo "OK  concise summary present"
else
  echo "FAIL summary missing"; fail=1
fi

echo
echo "=== TEST 2: firewall — noisy lines do not leak to stdout ==="
if echo "$OUT" | grep -q "$NOISE"; then
  echo "FAIL noisy sentinel leaked to stdout"; fail=1
else
  echo "OK  noise never reached stdout (only the summary did)"
fi

echo
echo "=== TEST 3: --input file mode works ==="
OUT2="$(python3 "$SCRIPT" --input "$BIG" --focus "first error")"
if echo "$OUT2" | grep -q "SUMMARY:" && ! echo "$OUT2" | grep -q "$NOISE"; then
  echo "OK  --input mode distilled, no leak"
else
  echo "FAIL --input mode output unexpected"; fail=1
fi

echo
echo "=== TEST 4: empty input is rejected ==="
if printf "" | python3 "$SCRIPT" --focus "x" >/dev/null 2>"$SANDBOX/err.log"; then
  echo "FAIL expected non-zero exit on empty input"; fail=1
else
  grep -q "ERROR" "$SANDBOX/err.log" && echo "OK  empty input rejected cleanly" \
    || { echo "FAIL no error message on empty input"; fail=1; }
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "########## ALL TESTS PASSED ##########"
else
  echo "########## THERE ARE FAILURES (see above) ##########"; exit 1
fi
