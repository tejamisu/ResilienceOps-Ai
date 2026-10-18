#!/usr/bin/env bash
# Re-runnable security check for the ResilienceOps API.
# Stands up a LOCAL, keyless copy of the backend (so no Gemini quota is ever spent and the real
# runs/ data is never touched), runs the attack probes against it, prints a pass/fail table, and tears down.
#
# Run from anywhere:   bash backend/tests/security/run_security_tests.sh
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
BACKEND="$(cd "$HERE/../.." && pwd)"
PY="${PYTHON:-$BACKEND/.venv/bin/python}"
PORT="${PORT:-8097}"
TMP="$(mktemp -d)"
trap 'kill "${SRV_PID:-0}" 2>/dev/null || true; rm -rf "$TMP"' EXIT

# isolated copy: code + data only, empty runs/, empty key
cp -R "$BACKEND/agents" "$BACKEND/core" "$BACKEND/data" "$BACKEND/api.py" "$BACKEND/main.py" "$TMP/"
mkdir -p "$TMP/runs"
printf 'GOOGLE_API_KEY=\nSTORE=local\n' > "$TMP/.env"

( cd "$TMP" && GOOGLE_API_KEY= STORE=local "$PY" -m uvicorn api:app --port "$PORT" --host 127.0.0.1 >"$TMP/server.log" 2>&1 ) &
SRV_PID=$!

# wait for a real 200 from health (uvicorn + ADK imports can take a few seconds)
up=""
for _ in $(seq 1 60); do
  code="$(curl -s -m2 -o /dev/null -w '%{http_code}' "http://127.0.0.1:$PORT/api/health" 2>/dev/null || true)"
  if [ "$code" = "200" ]; then up=1; break; fi
  sleep 0.5
done
if [ -z "$up" ]; then echo "server did not come up; log:"; cat "$TMP/server.log"; exit 1; fi

echo "== ResilienceOps API security probes (local, keyless) =="
"$PY" -I "$HERE/attack_api.py" "http://127.0.0.1:$PORT" > "$TMP/result.json"
"$PY" - "$TMP/result.json" <<'PY'
import sys, json
rows = json.load(open(sys.argv[1]))
bad = [r for r in rows if r["verdict"] == "OPEN" and r["id"] not in ("3","5","6b") and not r["id"].startswith("1a")]
print(f"{'ID':<6}{'VERDICT':<8}{'NAME'}")
for r in rows:
    print(f"{r['id'][:5]:<6}{r['verdict']:<8}{r['name']}")
print()
# 1a (public reads) and 3/5 (role fields with no login) are accepted residual risks for this public demo.
print("Accepted residual (by design, no login): public GET reads [1a], role/author on decisions [3,5], rate-limited Regenerate [6b].")
if bad:
    print(f"\nFAIL: {len(bad)} unexpected OPEN finding(s):", ", ".join(r['id'] for r in bad))
    sys.exit(1)
print("\nPASS: no unexpected OPEN findings.")
PY
