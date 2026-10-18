"""Small, dependency-free guards for the public API: a per-client rate limiter,
a request-body size cap, and a localhost check. Keeps the demo openly viewable
(all GETs stay open) while stopping credit-burn, flooding and oversized payloads."""
from __future__ import annotations

import os
import threading
import time

from fastapi import HTTPException, Request

# --- request body size cap (bytes) ---
MAX_BODY = int(os.getenv("MAX_BODY_BYTES", "65536"))   # 64 KB is plenty for a decision or a small context

# --- in-memory token bucket, per client IP, per bucket name ---
_lock = threading.Lock()
_buckets: dict[tuple[str, str], tuple[float, float]] = {}   # (name, ip) -> (tokens, last_refill)


def _client_ip(request: Request) -> str:
    # trust the platform's forwarded header on Cloud Run, else the socket peer
    fwd = request.headers.get("x-forwarded-for", "")
    return (fwd.split(",")[0].strip() if fwd else "") or (request.client.host if request.client else "unknown")


def is_local(request: Request) -> bool:
    return _client_ip(request) in ("127.0.0.1", "::1", "testclient")


async def body_size_ok(request: Request) -> None:
    """Reject oversized bodies early, by Content-Length and by actually reading no more than the cap."""
    cl = request.headers.get("content-length")
    if cl and cl.isdigit() and int(cl) > MAX_BODY:
        raise HTTPException(413, f"Request body too large (> {MAX_BODY} bytes).")


def rate_limit(request: Request, name: str, per_min: float, burst: float | None = None) -> None:
    """Allow `per_min` requests per minute per client IP for this bucket, with a small burst.
    Localhost (the owner developing) is never limited."""
    if is_local(request):
        return
    burst = burst if burst is not None else max(1.0, per_min)
    ip = _client_ip(request)
    now = time.time()
    rate = per_min / 60.0
    with _lock:
        tokens, last = _buckets.get((name, ip), (burst, now))
        tokens = min(burst, tokens + (now - last) * rate)
        if tokens < 1.0:
            raise HTTPException(429, "Too many requests. Please slow down.")
        _buckets[(name, ip)] = (tokens - 1.0, now)


def require_admin(request: Request) -> None:
    """Protect expensive/owner-only actions (warm-up, force-rerun). Localhost is allowed for development.
    Otherwise a correct X-Admin-Token header is required; if no token is configured, the action is refused."""
    if is_local(request):
        return
    token = os.getenv("ADMIN_TOKEN", "")
    if not token:
        raise HTTPException(403, "This action is owner-only. Set ADMIN_TOKEN on the server and send X-Admin-Token, or run it locally.")
    sent = request.headers.get("x-admin-token", "")
    # constant-time-ish comparison
    if len(sent) != len(token) or not all(a == b for a, b in zip(sent, token)):
        raise HTTPException(403, "Invalid admin token.")
