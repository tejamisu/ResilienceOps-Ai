#!/usr/bin/env python3
"""ResilienceOps — API security probes (run against a LOCAL, keyless test server only).

Each probe returns a row: id, group, name, request, response (trimmed), and verdict:
  OPEN     = the attack worked / the surface is exploitable as-is
  SAFE     = the server refused or the surface does not exist
  INFO     = reachable but gated elsewhere (e.g. needs a Gemini key to cost money)
Tokens/keys are masked. No external hosts are touched.

Usage:  attack_api.py http://127.0.0.1:8099
"""
import sys, json, re, time, urllib.request, urllib.error, concurrent.futures as cf

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8099"
rows = []
# simulate an external attacker (the server trusts X-Forwarded-For on Cloud Run); gates must engage for non-local IPs
def rip(n): return {"X-Forwarded-For": f"203.0.113.{n}"}
REMOTE = rip(9)   # the flood IP

def mask(s):
    s = str(s)
    s = re.sub(r'(AIza[0-9A-Za-z_\-]{6})[0-9A-Za-z_\-]+', r'\1…MASKED', s)
    return s

def call(method, path, body=None, headers=None, timeout=10):
    url = BASE + path
    data = json.dumps(body).encode() if body is not None else None
    h = {"content-type": "application/json"}
    if headers: h.update(headers)
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read().decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read().decode(errors="replace")
    except Exception as e:
        return None, {}, f"{type(e).__name__}: {e}"

def row(id, group, name, req, status, body, verdict, note=""):
    rows.append({"id": id, "group": group, "name": name, "request": req,
                 "status": status, "response": mask(str(body))[:300], "verdict": verdict, "note": note})

# ---- Group 1: impersonation / access control ----
# 1a: every endpoint reachable with no credentials
for p in ["/api/health", "/api/agents", "/api/scenario", "/api/decisions",
          "/api/agents/forecast_impact", "/api/warm"]:
    st, hd, bd = call("GET", p)
    row("1a:"+p, "impersonation", "unauthenticated GET "+p, f"GET {p} (no auth)",
        st, bd, "OPEN" if st == 200 else ("INFO" if st else "SAFE"),
        "all data endpoints answer with no login" if st == 200 else "")

# 3: role spoofing — analyst posts an approval AS the Incident Commander
spoof = {"action": "approve", "item": "SECTEST dispatch approval",
         "by": "Ananya Menon", "role": "Incident Commander", "phase": "respond",
         "detail": "posted by SECTEST pretending to be the IC"}
st, hd, bd = call("POST", "/api/decisions", spoof, rip(11))
row("3", "impersonation", "role spoof on /api/decisions", "POST /api/decisions by='Ananya Menon' role='Incident Commander'",
    st, bd, "OPEN" if st == 200 else "SAFE", "server stores whatever by/role the client claims")

# 5: bypass disabled UI — post an approval the Analyst role is blocked from in the UI
st, hd, bd = call("POST", "/api/decisions", {"action": "approve", "item": "SECTEST analyst-forced approval",
    "by": "Dr. Rahul Nair", "role": "Hazard Analyst", "detail": "UI blocks this; API does not"}, rip(12))
row("5", "limits", "approval via API despite UI lock", "POST /api/decisions as Hazard Analyst (UI-locked action)",
    st, bd, "OPEN" if st == 200 else "SAFE", "no server-side role check on decisions")

# 2: try to delete / overwrite another actor's data
st_d, _, bd_d = call("DELETE", "/api/decisions")
st_p, _, bd_p = call("PUT", "/api/decisions", {"x": 1})
row("2", "impersonation", "delete/overwrite others' decisions",
    "DELETE /api/decisions ; PUT /api/decisions",
    f"{st_d}/{st_p}", f"DELETE={bd_d[:80]} PUT={bd_p[:80]}",
    "SAFE" if st_d in (404,405) and st_p in (404,405) else "OPEN",
    "log is append-only; no edit/delete endpoint")

# ---- Group 2: getting around limits ----
# 6: credit-spending endpoints reachable with no auth
st, hd, bd = call("POST", "/api/warm", headers=rip(13))
# 503 here = only because this test server has no key; the point is there's no auth BEFORE that check
row("6a", "limits", "unauth POST /api/warm (credit burn)", "POST /api/warm (no auth)",
    st, bd, "INFO" if st == 503 else ("OPEN" if st in (200,202) else "SAFE"),
    "no auth gate; 503 only because THIS test server has no key — with a key it spends the owner's quota")
st, hd, bd = call("POST", "/api/agents/forecast_impact/run", {"context": {}}, rip(14))
src = ""
try: src = json.loads(bd).get("source")
except Exception: pass
row("6b", "limits", "unauth POST /run reaches the model path", "POST /api/agents/forecast_impact/run (no auth)",
    st, f"source={src}", "OPEN" if st == 200 else "SAFE",
    "reaches runner unauthenticated; with a key each call spends quota (here falls back to rules)")

# 7: 20 concurrent writes — do they all succeed and is the file left valid?
def one(i):
    return call("POST", "/api/agents/forecast_impact/run", {"context": {}}, rip(14))[0]
with cf.ThreadPoolExecutor(max_workers=20) as ex:
    codes = list(ex.map(one, range(20)))
ok = sum(1 for c in codes if c == 200)
blocked = sum(1 for c in codes if c == 429)
row("7", "limits", "20 concurrent /run (credit-burn flood)", "20x POST /run in parallel (remote IP)",
    f"{ok} ok / {blocked} blocked", f"excess rate-limited = {blocked>0}",
    "OPEN" if ok == 20 else "SAFE",
    "no rate limit: every call would spend quota" if ok==20 else f"rate limit engaged: only {ok} ran, {blocked} refused (429)")
# integrity: fire 20 valid decisions in parallel and confirm the log stays valid JSON
def oned(i):
    return call("POST", "/api/decisions", {"action": "note", "item": f"SECTEST flood {i}", "detail": "x"*50}, rip(100+i))[0]
with cf.ThreadPoolExecutor(max_workers=20) as ex:
    dcodes = list(ex.map(oned, range(20)))
st, _, bd = call("GET", "/api/decisions")
try: valid = isinstance(json.loads(bd).get("decisions"), list)
except Exception: valid = False
row("7b", "limits", "concurrent writes keep the log valid", "20x POST /api/decisions in parallel",
    f"{sum(1 for c in dcodes if c==200)} ok", f"log valid JSON = {valid}",
    "SAFE" if valid else "OPEN", "file lock keeps the log valid" if valid else "LOG CORRUPTED")

# 8: oversized / malformed input
big = {"action": "A"*200000, "item": "SECTEST big", "detail": "B"*500000}
st, _, bd = call("POST", "/api/decisions", big, rip(15))
row("8a", "limits", "oversized strings accepted", "POST /api/decisions with ~700KB of text",
    st, f"{len(bd)}b resp", "OPEN" if st == 200 else "SAFE", "no max length on any string field")
st, _, bd = call("POST", "/api/decisions", {"action": None, "item": 12345, "by": {"$ne": 1}})
row("8b", "limits", "wrong types", "POST /api/decisions action=null item=int by=object",
    st, bd, "SAFE" if st == 422 else "OPEN", "pydantic rejects wrong types" if st == 422 else "accepts malformed")
st, _, bd = call("POST", "/api/agents/forecast_impact/run", {"context": {"evil": "x"*300000, "n": -999999}}, rip(16))
row("8c", "limits", "unbounded context dict", "POST /run with a huge/negative context",
    st, f"status {st}", "OPEN" if st == 200 else "SAFE", "context: dict has no schema/size limit")

# unknown agent handling
st, _, bd = call("GET", "/api/agents/__proto__")
row("8d", "limits", "unknown agent name", "GET /api/agents/__proto__",
    st, bd, "SAFE" if st == 404 else "OPEN", "")

# ---- Group 3: from outside ----
# CORS: is any origin allowed?
st, hd, bd = call("GET", "/api/health", headers={"Origin": "https://evil.example"})
aco = hd.get("access-control-allow-origin") or hd.get("Access-Control-Allow-Origin")
row("12", "outside", "CORS allows any origin", "GET /api/health with Origin: https://evil.example",
    st, f"Access-Control-Allow-Origin={aco}", "OPEN" if aco in ("*", "https://evil.example") else "SAFE",
    "any website can read these responses from a victim's browser")

# SSRF: is there any endpoint that fetches a user URL?
st, _, bd = call("POST", "/api/agents/forecast_impact/run", {"context": {"url": "http://169.254.169.254/latest/meta-data/"}})
fetched = "169.254" in bd or "meta-data" in bd
row("11", "outside", "SSRF via context url", "POST /run context.url=http://169.254.169.254/…",
    st, "no server-side fetch of the url" if not fetched else "URL was fetched",
    "SAFE" if not fetched else "OPEN", "no endpoint fetches user-supplied URLs")

print(json.dumps(rows, indent=2, ensure_ascii=False))
