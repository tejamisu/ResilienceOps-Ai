"""The Wayanad scenario (data/wayanad.json): one source for every agent and for the app's screens."""
from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data" / "wayanad.json"


@lru_cache(maxsize=1)
def scenario() -> dict:
    with open(DATA, encoding="utf-8") as f:
        return json.load(f)


def place(place_id: str) -> dict:
    for p in scenario()["places"]:
        if p["id"] == place_id:
            return p
    raise KeyError(f"Unknown place '{place_id}'. Known: {[p['id'] for p in scenario()['places']]}")


def community(cid: str) -> dict:
    for c in scenario()["communities"]:
        if c["id"] == cid:
            return c
    raise KeyError(f"Unknown community '{cid}'.")


def team(tid: str) -> dict:
    for t in scenario()["teams"]:
        if t["id"] == tid:
            return t
    raise KeyError(f"Unknown team '{tid}'.")
