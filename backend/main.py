"""ResilienceOps AI — command line.

  python main.py --list                 list the agents
  python main.py forecast_impact        run one agent (Gemini if GOOGLE_API_KEY is set, else rule-written text)
  python main.py --all                  run every agent in lifecycle order and save the results to runs/
  python main.py --rules dispatch       force the rule-written version (no API call)
"""
from __future__ import annotations

import argparse
import asyncio
import json
import warnings

from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

from agents import AGENTS  # noqa: E402
from core import runner, store  # noqa: E402


def show(res: dict) -> None:
    print(f"\n=== {res['display']} · {res['phase']} · text by {res['source']}{' (' + res['model'] + ')' if res.get('model') else ''} · {res['duration_s']} s")
    if res.get("error"):
        print("   note:", res["error"])
    if res["tool_calls"]:
        print("   tools called:", ", ".join(res["tool_calls"]))
    print(json.dumps(res["text"], ensure_ascii=False, indent=2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("agent", nargs="?")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--rules", action="store_true")
    ap.add_argument("--staged", action="store_true", help="dispatch: Rescue Unit 2 was staged at Meppadi by Prepare")
    a = ap.parse_args()
    if a.list or not (a.agent or a.all):
        for n, m in AGENTS.items():
            print(f"{n:18} {m.DISPLAY:34} {m.PHASE:8} owner: {m.OWNER}")
        print("\nGemini configured:", runner.has_key())
        return
    names = list(AGENTS) if a.all else [a.agent]
    ctx = {"staged": True} if a.staged else {}
    for n in names:
        mod = AGENTS[n]
        res = runner.run_rules(mod, ctx) if a.rules else asyncio.run(runner.run_gemini(mod, ctx))
        show(res)
        if a.all and res["source"] == "gemini":
            store.save_run(n, res)


if __name__ == "__main__":
    main()
