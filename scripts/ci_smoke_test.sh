#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0
FAIL=0

run() {
    local desc="$1"; shift
    printf "  %-50s" "$desc"
    if "$@" >/dev/null 2>&1; then
        echo "[OK]"
        PASS=$((PASS + 1))
    else
        echo "[FAIL]"
        FAIL=$((FAIL + 1))
    fi
}

echo "PRG32 Host Smoke Test"
echo

echo "Python syntax checks"
for py in "$REPO_ROOT"/tools/*.py; do
    run "$(basename "$py")" python3 -m py_compile "$py"
done
echo

echo "Whitespace checks"
run "git diff --check" bash -c "cd '$REPO_ROOT' && git diff --check"
echo

echo "ABI generated files"
run "prg32_abi_gen.py --check" python3 "$REPO_ROOT/tools/prg32_abi_gen.py" --check
echo

echo "Cartridge tool doctor"
run "prg32_game.py doctor" python3 "$REPO_ROOT/tools/prg32_game.py" doctor --host-only
echo

echo "Results: $PASS passed, $FAIL failed"
if [ "$FAIL" -gt 0 ]; then
    echo "SMOKE TEST FAILED"
    exit 1
fi
echo "SMOKE TEST PASSED"
