"""Offline tests: no API key needed. Run with:  python -m pytest -q   (or python tests/test_agents.py)"""
import asyncio
import os
import sys
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents import AGENTS
from core import runner


def test_every_tool_has_a_gemini_schema():
    from google.adk.tools import FunctionTool
    for m in AGENTS.values():
        for t in m.TOOLS:
            FunctionTool(t)._get_declaration()


def test_every_agent_runs_on_rules_and_fills_its_text_contract():
    for m in AGENTS.values():
        r = runner.run_rules(m, {})
        assert r["source"] == "rules" and r["facts"] and r["text"]
        assert set(m.TEXT_SPEC) <= set(r["text"]), (m.NAME, set(m.TEXT_SPEC) - set(r["text"]))
        assert {"recommendation", "evidence", "confidence"} <= set(r["trace"])


def test_ranking_matches_the_app():
    f = AGENTS["forecast_impact"].facts({})
    assert [(p["place"], p["level"]) for p in f["places"]] == [("meppadi", "Critical"), ("vythiri", "High"), ("mananthavady", "High"), ("kalpetta", "Moderate")]


def test_dispatch_uses_the_prepare_handover():
    d = AGENTS["dispatch"]
    assert d.facts({})["lead"]["team"] == "fr2" and d.facts({})["eta_min"] == 26
    assert d.facts({"staged": True})["eta_min"] == 11
    assert d.facts({})["support"]["team"] == "jcb3" and d.facts({"staged": True})["support"]["team"] == "jcb3"


def test_relief_coverage_finds_chooralmala():
    assert [m["id"] for m in AGENTS["relief_coverage"].facts({})["missed"]] == ["chooralmala"]


def test_gemini_path_without_a_key_falls_back_to_rules():
    os.environ.pop("GOOGLE_API_KEY", None)
    r = asyncio.run(runner.run_gemini(AGENTS["forecast_impact"], {}))
    assert r["source"] == "rules" and "not set" in r["error"]


def test_model_answer_is_merged_safely():
    base = {"a": "rule", "b": {"x": "rule"}, "c": ["r1"]}
    got = runner._merge(base, runner._json_from('```json\n{"a": "model", "b": {"x": ""}, "c": ["m1", "m2"], "junk": 1}\n```'))
    assert got == {"a": "model", "b": {"x": "rule"}, "c": ["m1", "m2"]}


if __name__ == "__main__":
    for n, f in list(globals().items()):
        if n.startswith("test_"):
            f(); print("ok", n)
