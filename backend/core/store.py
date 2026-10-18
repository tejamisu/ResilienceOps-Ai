"""Small store: the latest run of each agent, and the decision log (approvals, edits, sends).
Default: local JSON files in runs/ (per Cloud Run instance; reset on redeploy).
Set STORE=firestore (and GOOGLE_CLOUD_PROJECT on Cloud Run) to keep them in Firestore: collections `runs` and `decisions`."""
from __future__ import annotations

import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path

RUNS = Path(__file__).resolve().parent.parent / "runs"
RUNS.mkdir(exist_ok=True)
_lock = threading.Lock()
MAX_DECISIONS = int(os.getenv("MAX_DECISIONS", "2000"))   # bound the local decision log


def _read(path: Path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default


_fs = None
if os.getenv("STORE", "").lower() == "firestore":
    try:
        from google.cloud import firestore   # pip install google-cloud-firestore
        _fs = firestore.Client()
    except Exception as e:  # missing library or credentials: keep the local files, say so once
        print(f"[store] Firestore unavailable ({e}); using local files in runs/")


def save_run(agent: str, result: dict) -> None:
    if _fs:
        _fs.collection("runs").document(agent).set(result)
        return
    with _lock:
        with open(RUNS / f"{agent}.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)


def load_run(agent: str) -> dict | None:
    if _fs:
        d = _fs.collection("runs").document(agent).get()
        return d.to_dict() if d.exists else None
    return _read(RUNS / f"{agent}.json", None)


def add_decision(entry: dict) -> dict:
    if _fs:
        entry = {**entry, "recorded_at": datetime.now(timezone.utc).isoformat()}
        _fs.collection("decisions").add(entry)
        return entry
    with _lock:
        log = _read(RUNS / "decisions.json", [])
        if not isinstance(log, list):
            log = []
        entry = {**entry, "recorded_at": datetime.now(timezone.utc).isoformat()}
        log.append(entry)
        log = log[-MAX_DECISIONS:]   # keep the log bounded (newest kept) so it can't grow without limit
        with open(RUNS / "decisions.json", "w", encoding="utf-8") as f:
            json.dump(log, f, ensure_ascii=False, indent=2)
    return entry


def decisions() -> list:
    if _fs:
        return [d.to_dict() for d in _fs.collection("decisions").order_by("recorded_at").stream()]
    return _read(RUNS / "decisions.json", [])
