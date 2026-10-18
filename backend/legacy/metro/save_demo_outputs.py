"""
Save pre-canned demo outputs for all 9 ResilienceOps AI agents.

Run once when you have API access. The outputs are saved to demo_outputs/
so the system can be demonstrated offline without calling the API.

Usage:
    python save_demo_outputs.py                  # Run all agents
    python save_demo_outputs.py --agent sentinel  # Run one agent
    python save_demo_outputs.py --dry-run         # Show what would run
"""

import os
import sys
import json
import argparse
import datetime

from dotenv import load_dotenv
load_dotenv()

if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not set. Run:  echo 'GOOGLE_API_KEY=your_key' > .env")
    sys.exit(1)

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "demo_outputs")

DEMO_SEQUENCE = [
    "risk_memory",
    "sentinel",
    "preparedness",
    "triage",
    "field_intel",
    "dispatch",
    "communication",
    "damage_assessment",
    "reconciliation",
]

AGENT_PROMPTS = {
    "sentinel": (
        "An IMD RED alert has just been issued for extremely heavy rainfall "
        "in the next 18 hours. Analyze all ward risk, prioritize the wards, "
        "estimate population exposure, and generate the preparedness plan."
    ),
    "triage": (
        "Process all incoming alerts and field reports and produce the "
        "prioritized incident queue for the command centre."
    ),
    "field_intel": (
        "Process this field report: 'Water has entered ground floor near Sector 8 "
        "clinic, Ward 12. Two elderly residents trapped. Route A appears flooded.' "
        "Source: Community volunteer. Location: Ward 12 Sector 8."
        " Then show all active field reports."
    ),
    "dispatch": (
        "We have a CRITICAL incident in Ward 12 Sector 8 — trapped elderly residents "
        "near the clinic. And a CRITICAL route blockage in Ward 19 — Route F submerged. "
        "Provide dispatch recommendations for both incidents."
    ),
    "communication": (
        "Draft a multilingual public safety advisory for Ward 12 (CRITICAL flood). "
        "Shelter B is open at School W12-A. Route A is flooded — use Route C. "
        "Also draft a State EOC escalation notification requesting 4 pumps and 1 boat. "
        "Provide in English, Hindi, and Marathi."
    ),
    "damage_assessment": (
        "The flood event in Metro District has peaked and is receding. "
        "Provide the damage and needs assessment with relief coverage status "
        "and identify any communities not yet receiving aid."
    ),
    "reconciliation": (
        "Compare our pre-event Sentinel predictions with what actually happened "
        "during the flood. Identify model accuracy, gaps, and produce the "
        "after-action improvement recommendations."
    ),
    "risk_memory": (
        "Retrieve the historical flood risk profile for Ward 12 and Ward 19. "
        "What are the recurring hotspots and what have we learned from past events?"
    ),
    "preparedness": (
        "Based on this year's flood event and historical data, what are the "
        "critical pre-monsoon preparedness tasks for next season?"
    ),
}

PHASE_LABELS = {
    "risk_memory":       "Phase 1 — Forecast & Prepare",
    "sentinel":          "Phase 1 — Forecast & Prepare",
    "preparedness":      "Phase 1 — Forecast & Prepare",
    "triage":            "Phase 2 — Live Response",
    "field_intel":       "Phase 2 — Live Response",
    "dispatch":          "Phase 2 — Live Response",
    "communication":     "Phase 2 — Live Response",
    "damage_assessment": "Phase 3 — Recover & Improve",
    "reconciliation":    "Phase 3 — Recover & Improve",
}


def save_agent_output(agent_name: str, output: str, prompt: str) -> str:
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    record = {
        "agent": agent_name,
        "phase": PHASE_LABELS.get(agent_name, "Unknown"),
        "prompt": prompt,
        "output": output,
        "captured_at": datetime.datetime.now().isoformat(),
        "model": "gemini-3.8-flash",
    }
    path = os.path.join(OUTPUT_DIR, f"{agent_name}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2, ensure_ascii=False)
    return path


def load_demo_output(agent_name: str):
    path = os.path.join(OUTPUT_DIR, f"{agent_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def run_and_save(agent_name: str, rate_limit_pause: int = 120) -> bool:
    from orchestrator import ResilienceOpsCoordinator
    import time

    prompt = AGENT_PROMPTS[agent_name]
    print(f"\n[{agent_name}] Running...")
    try:
        coordinator = ResilienceOpsCoordinator()
        output = coordinator.run_agent(agent_name, prompt, retries=5)
        path = save_agent_output(agent_name, output, prompt)
        lines = output.count("\n") + 1
        print(f"[{agent_name}] Saved — {lines} lines → {path}")
        # Respect free-tier 5 RPM limit between agents
        print(f"  [waiting {rate_limit_pause}s before next agent...]")
        time.sleep(rate_limit_pause)
        return True
    except Exception as e:
        print(f"[{agent_name}] FAILED: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Save pre-canned demo outputs for ResilienceOps AI")
    parser.add_argument("--agent", type=str, help="Run a specific agent only")
    parser.add_argument("--dry-run", action="store_true", help="Show what would run without calling the API")
    parser.add_argument("--force", action="store_true", help="Overwrite existing outputs")
    args = parser.parse_args()

    agents_to_run = [args.agent] if args.agent else DEMO_SEQUENCE

    if args.dry_run:
        print("\nWould run the following agents:")
        for name in agents_to_run:
            path = os.path.join(OUTPUT_DIR, f"{name}.json")
            status = "EXISTS" if os.path.exists(path) else "MISSING"
            print(f"  {name:<22} [{status}]")
        return

    print(f"\nSaving demo outputs to: {OUTPUT_DIR}/")
    print(f"Agents: {', '.join(agents_to_run)}\n")

    passed, failed, skipped = [], [], []
    for name in agents_to_run:
        path = os.path.join(OUTPUT_DIR, f"{name}.json")
        if os.path.exists(path) and not args.force:
            print(f"[{name}] SKIP — already exists (use --force to overwrite)")
            skipped.append(name)
            continue
        ok = run_and_save(name)
        (passed if ok else failed).append(name)

    print(f"\n{'='*50}")
    print(f"Done: {len(passed)} saved, {len(skipped)} skipped, {len(failed)} failed")
    if failed:
        print(f"Failed: {', '.join(failed)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
