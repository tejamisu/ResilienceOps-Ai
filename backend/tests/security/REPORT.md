# ResilienceOps — security self-test (before / after)

Date: 18 Oct 2026 · Tester: automated probes on a **local, keyless** copy of the backend
(no Gemini quota spent, the real `runs/` data never touched). Re-run any time with:

```bash
bash backend/tests/security/run_security_tests.sh
```

The app is a **public demo** for the AI Builder Cup: the judges open the link with no login, so the
goal is not to lock it behind auth. It is to stop the things that actually cost money or mislead —
credit burn, a backend that can be repointed, oversized/garbage input, and injected markup — while
leaving the demo openly viewable.

Tokens and keys are masked in all output. Every row below was **executed**, not read from the code.

## Results

| # | Attack (the 14, mapped to this app) | Before | After | What changed |
|---|---|---|---|---|
| 1 | Call every `/api/*` with no login | OPEN | OPEN · accepted | Public demo: reads stay open (health, agents, scenario, decisions). No secrets are exposed. |
| 2 | Delete or overwrite another actor's decisions | SAFE | SAFE | Log is append-only; there is no edit/delete endpoint. |
| 3 | Role-spoof a decision (post as the IC) | OPEN | OPEN · residual | No login, so a *valid* role can still be claimed. But markup, unknown roles, and extra fields are now **rejected (422)**, and the log is never rendered or trusted. |
| 4 | Reuse a password-reset link | N/A | N/A | There is no auth/reset flow. |
| 5 | Make a UI-locked approval via the API | OPEN | OPEN · residual | Same as #3 — the decision log is a record of the demo, not an authenticated control. |
| 6 | Burn Gemini credits via `/warm` and `/run` | OPEN | **FIXED / residual** | `/warm` (and `?force=1`) is now **owner-only** (`X-Admin-Token`, or localhost) → remote callers get 403. `/run` (the Regenerate button) stays usable but is **rate-limited**. |
| 7 | 20 concurrent `/run` (credit flood) | OPEN | **FIXED** | Rate limit engages: only ~9 of 20 run, the rest get **429**. Concurrent decision writes still leave the log valid (file lock). |
| 8 | Oversized / malformed / negative input | OPEN | **FIXED** | 64 KB body cap; every `Decision` field length-bounded; `context` capped at 4 KB; unknown fields rejected; wrong types already gave 422. |
| 9 | `?api=` repoints the backend, sticky | **OPEN (serious)** | **FIXED** | On a deployed (non-localhost) page, `?api=` and any saved override are **ignored** — the app always uses its own origin. Still honoured on `localhost`/`file://` for development. |
| 10 | `<img onerror>` stored XSS | SAFE | SAFE | Verified live: a planted payload in an agent's text and in a decision renders as **literal text**; `onerror` never fires. The frontend escapes every external string. |
| 11 | SSRF via a supplied URL | SAFE | SAFE | No endpoint fetches a user-supplied URL. |
| 12 | CORS allows any origin | OPEN | **FIXED** | `Access-Control-Allow-Origin: *` removed. Default is the local dev origins only; add production origins with `CORS_ORIGINS`. (The app is same-origin, so it needs none.) |

Suite verdict: **PASS** — no unexpected OPEN findings. The three residuals (1, 3/5, and the
rate-limited Regenerate) are accepted and documented above.

## How each fix was proven (protection off → attack works; on → refused)

- **#9 `?api=` override** — loaded the real built app from a non-localhost host
  (`http://192.168.1.12:…/resilienceops.html?api=http://attacker`): the app **ignored** it
  (`RO_API.base === ""`, nothing saved). From `http://127.0.0.1` the same link is still honoured
  (dev workflow intact). Before the fix, one visit repointed the backend and **persisted** across
  later plain visits.
- **#10 XSS** — planted `<img src=x onerror=…>` in a saved agent run and in a decision, loaded the
  Audit view: `window.__xss === 0`, the payload appeared as `&lt;img…` text, zero `<img>` tags created.
- **#6 / #7 credit burn** — as a remote IP, `POST /api/warm` → **403** (owner-only);
  20× `POST /run` → **9 ran, 11 refused (429)**. From localhost both are allowed (owner development).
- **#8 input** — `POST /api/decisions` with ~700 KB → **413**; markup/unknown role/extra field → **422**;
  a valid `{"action":"note","item":"ok"}` → **200**.
- **#12 CORS** — `GET /api/health` with `Origin: https://evil.example` → **no** `Access-Control-Allow-Origin`.

## Files changed

- `backend/core/guard.py` *(new)* — per-IP rate limiter, body-size cap, localhost check, admin gate.
- `backend/api.py` — CORS allowlist (no `*`); `Decision` and `RunBody` validated and size-bounded;
  rate limits on `/run` and `/api/decisions`; `/api/warm` owner-gated.
- `backend/core/store.py` — decision log bounded (`MAX_DECISIONS`, default 2000).
- `test-run/api-client.js` — `?api=` override honoured on localhost only; never persisted in production.

## Two steps for you (owner-only)

1. **Warm-up in production now needs the admin token.** Generate one, store it as a secret, and
   pass it on deploy and when warming:

   ```bash
   # create the token secret (run once)
   python3 -c "import secrets; print(secrets.token_urlsafe(24))" | tr -d '\n' | gcloud secrets create admin-token --data-file=-
   # let Cloud Run read it (same service account as the Gemini secret)
   NUM=$(gcloud projects describe $(gcloud config get-value project) --format='value(projectNumber)')
   gcloud secrets add-iam-policy-binding admin-token --member="serviceAccount:${NUM}-compute@developer.gserviceaccount.com" --role=roles/secretmanager.secretAccessor
   ```

   Add `ADMIN_TOKEN` to the deploy command's secrets:

   ```bash
   gcloud run deploy resilienceops --source . --allow-unauthenticated \
     --set-secrets GOOGLE_API_KEY=gemini-api-key:latest,ADMIN_TOKEN=admin-token:latest
   ```

   Then warm with the header (read the token back from the secret):

   ```bash
   TOKEN=$(gcloud secrets versions access latest --secret=admin-token)
   curl -X POST -H "X-Admin-Token: $TOKEN" https://YOUR-SERVICE-URL/api/warm
   ```

   (Or skip all of this and warm from your Mac against `http://localhost:8080`, which is exempt.)

2. **Optional — install Anthropic's security-guidance plugin** for ongoing review:
   `/plugin install security-guidance@claude-plugins-official`. These reviews use extra usage.
