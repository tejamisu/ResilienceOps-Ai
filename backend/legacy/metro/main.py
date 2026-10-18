"""
ResilienceOps AI — Main Entry Point

Demonstrates the full multi-agent system through a realistic urban flood
scenario: IMD RED alert → Sentinel risk assessment → live response → recovery.

Usage:
    python main.py                  # Full demo walkthrough
    python main.py --agent sentinel # Run only the Sentinel agent
    python main.py --agent triage   # Run only the Triage agent
    python main.py --list           # List all available agents
"""

import os
import sys
import argparse
from dotenv import load_dotenv

load_dotenv()

# Verify API key is loaded from .env
if not os.getenv("GOOGLE_API_KEY"):
    print("ERROR: GOOGLE_API_KEY not set.")
    print("Run:  echo 'GOOGLE_API_KEY=your_key' > .env")
    sys.exit(1)

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    from rich.text import Text
    HAS_RICH = True
except ImportError:
    HAS_RICH = False

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
        "Also draft a State EOC escalation notification requesting 4 pumps and 1 boat."
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

PHASE_DESCRIPTIONS = {
    "sentinel": ("PHASE 1: FORECAST & PREPARE", "Sentinel Agent analyzing IMD RED alert..."),
    "triage": ("PHASE 2: LIVE RESPONSE — Alert Triage", "Triage Agent processing incoming reports..."),
    "field_intel": ("PHASE 2: LIVE RESPONSE — Field Intelligence", "Field Intel Agent processing reports..."),
    "dispatch": ("PHASE 2: LIVE RESPONSE — Dispatch", "Dispatch Agent generating recommendations..."),
    "communication": ("PHASE 2: LIVE RESPONSE — Communications", "Communication Agent drafting advisories..."),
    "damage_assessment": ("PHASE 3: RECOVER — Damage & Needs", "Damage Assessment Agent analyzing post-flood data..."),
    "reconciliation": ("PHASE 3: RECOVER — Reconciliation", "Reconciliation Agent comparing predictions vs. reality..."),
    "risk_memory": ("PHASE 1: LEARN — Risk Memory", "Risk Memory Agent surfacing historical patterns..."),
    "preparedness": ("PHASE 1: LEARN — Preparedness Planning", "Preparedness Agent generating task list..."),
}


def print_header():
    if HAS_RICH:
        console = Console()
        console.print(Panel.fit(
            "[bold cyan]ResilienceOps AI[/bold cyan]\n"
            "[white]Multi-Agent Urban Flood Coordination Platform[/white]\n"
            "[dim]Hack2Skill Google Hackathon — Sustainability & Social Impact[/dim]",
            border_style="cyan",
        ))
    else:
        print("=" * 60)
        print("  ResilienceOps AI")
        print("  Multi-Agent Urban Flood Coordination Platform")
        print("=" * 60)


def run_single_agent(agent_name: str):
    from orchestrator import ResilienceOpsCoordinator

    console = Console() if HAS_RICH else None
    coordinator = ResilienceOpsCoordinator()

    phase_title, phase_desc = PHASE_DESCRIPTIONS.get(agent_name, (agent_name.upper(), f"Running {agent_name}..."))
    prompt = AGENT_PROMPTS.get(agent_name, "Provide your analysis.")

    if HAS_RICH:
        console.print(Rule(f"[bold yellow]{phase_title}[/bold yellow]"))
        console.print(f"[dim]{phase_desc}[/dim]\n")
    else:
        print(f"\n{'='*60}\n{phase_title}\n{phase_desc}\n{'='*60}")

    response = coordinator.run_agent(agent_name, prompt)

    if HAS_RICH:
        console.print(Panel(response, title=f"[green]{agent_name.upper()} AGENT OUTPUT[/green]", border_style="green"))
    else:
        print(f"\n--- {agent_name.upper()} OUTPUT ---\n{response}\n")


def run_full_demo():
    from orchestrator import ResilienceOpsCoordinator

    console = Console() if HAS_RICH else None
    coordinator = ResilienceOpsCoordinator()

    print_header()

    # Full demo: run agents in the order of the disaster lifecycle
    demo_sequence = [
        "risk_memory",
        "sentinel",
        "triage",
        "field_intel",
        "dispatch",
        "communication",
        "damage_assessment",
        "reconciliation",
        "preparedness",
    ]

    if HAS_RICH:
        console.print("\n[bold]Running full disaster lifecycle demo...[/bold]")
        console.print("[dim]Scenario: IMD RED Alert — Urban Flash Flood — Metro District[/dim]\n")
    else:
        print("\nRunning full disaster lifecycle demo...")
        print("Scenario: IMD RED Alert — Urban Flash Flood — Metro District\n")

    for agent_name in demo_sequence:
        phase_title, phase_desc = PHASE_DESCRIPTIONS[agent_name]
        prompt = AGENT_PROMPTS[agent_name]

        if HAS_RICH:
            console.print(Rule(f"[bold yellow]{phase_title}[/bold yellow]"))
            console.print(f"[dim]{phase_desc}[/dim]")
        else:
            print(f"\n{'='*60}\n{phase_title}\n{'='*60}")

        response = coordinator.run_agent(agent_name, prompt)

        if HAS_RICH:
            console.print(Panel(
                response,
                title=f"[green]{agent_name.replace('_', ' ').title()} Agent[/green]",
                border_style="green",
                expand=False,
            ))
            console.print()
        else:
            print(f"\n{response}\n{'-'*60}\n")


def main():
    parser = argparse.ArgumentParser(description="ResilienceOps AI — Multi-Agent Demo")
    parser.add_argument("--agent", type=str, help="Run a specific agent by name")
    parser.add_argument("--list", action="store_true", help="List all available agents")
    args = parser.parse_args()

    if args.list:
        print("\nAvailable agents:")
        for name, (phase, _) in PHASE_DESCRIPTIONS.items():
            print(f"  {name:<22} — {phase}")
        return

    print_header()

    if args.agent:
        if args.agent not in AGENT_PROMPTS:
            print(f"Unknown agent '{args.agent}'. Run with --list to see options.")
            sys.exit(1)
        run_single_agent(args.agent)
    else:
        run_full_demo()


if __name__ == "__main__":
    main()
