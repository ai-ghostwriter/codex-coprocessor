#!/usr/bin/env bash
#
# test_smoke.sh — Validate recon.py WITHOUT calling the real Codex.
#
# Stubs the `codex` binary with a fake that returns a canned distilled answer,
# and verifies the firewall property: a sentinel string living inside a target
# file must NOT appear on stdout (because recon.py passes the PATH to Codex and
# never reads the content itself), while the distilled answer MUST appear.
#
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPT="$HERE/recon.py"
SANDBOX="$(mktemp -d)"
BIN="$SANDBOX/bin"; mkdir -p "$BIN"
trap 'rm -rf "$SANDBOX"' EXIT

SENTINEL="RAWBYTES_THAT_MUST_NOT_LEAK_0xDEADBEEF"

# A big target file whose content must never reach stdout.
BIG="$SANDBOX/big.txt"
for i in $(seq 1 200); do echo "line $i $SENTINEL"; done > "$BIG"

# Stub codex: ignore the prompt, return only a distilled answer.
cat > "$BIN/codex" <<'STUB'
#!/usr/bin/env bash
echo "DISTILLED: the function refreshes the auth token and is called by 2 modules."
STUB
chmod +x "$BIN/codex"
export PATH="$BIN:$PATH"

fail=0
echo "=== TEST 1: read mode returns only the distilled answer ==="
OUT="$(python3 "$SCRIPT" "What does it do?" "$BIG" --mode read)"
echo "stdout: $OUT"
if echo "$OUT" | grep -q "DISTILLED:"; then
  echo "OK  distilled answer present"
else
  echo "FAIL distilled answer missing"; fail=1
fi

echo
echo "=== TEST 2: firewall — raw file content does not leak to stdout ==="
if echo "$OUT" | grep -q "$SENTINEL"; then
  echo "FAIL sentinel leaked to stdout (firewall breach)"; fail=1
else
  echo "OK  sentinel never reached stdout (firewall holds)"
fi

echo
echo "=== TEST 3: search and web modes also return only the distilled answer ==="
OUT2="$(python3 "$SCRIPT" "Where is X?" "$SANDBOX" --mode search --pattern "rate.?limit")"
OUT3="$(python3 "$SCRIPT" "What tiers?" "https://example.com/pricing" --mode web)"
if echo "$OUT2$OUT3" | grep -q "DISTILLED:" && ! echo "$OUT2$OUT3" | grep -q "$SENTINEL"; then
  echo "OK  search/web modes distilled, no leak"
else
  echo "FAIL search/web mode output unexpected"; fail=1
fi

echo
echo "=== TEST 4: codex failure surfaces a clean error ==="
cat > "$BIN/codex" <<'STUB'
#!/usr/bin/env bash
echo "boom" >&2
exit 1
STUB
chmod +x "$BIN/codex"
if python3 "$SCRIPT" "q" "$BIG" >/dev/null 2>"$SANDBOX/err.log"; then
  echo "FAIL expected non-zero exit on codex failure"; fail=1
else
  grep -q "ERROR" "$SANDBOX/err.log" && echo "OK  clean error on codex failure" \
    || { echo "FAIL no error message"; fail=1; }
fi

echo
if [ "$fail" -eq 0 ]; then
  echo "########## ALL TESTS PASSED ##########"
else
  echo "########## THERE ARE FAILURES (see above) ##########"; exit 1
fi
