"""
Show pre-saved demo outputs without calling the API.

Usage:
    python show_demo_output.py                   # Print all 9 in lifecycle order
    python show_demo_output.py --agent sentinel  # Print one agent
    python show_demo_output.py --list            # List what's saved
"""

import os
import json
import argparse

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

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    HAS_RICH = True
except ImportError:
    HAS_RICH = False


def load(agent_name: str):
    path = os.path.join(OUTPUT_DIR, f"{agent_name}.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def show(agent_name: str):
    data = load(agent_name)
    if data is None:
        print(f"[{agent_name}] No saved output found. Run: python save_demo_outputs.py --agent {agent_name}")
        return

    phase = data.get("phase", "")
    output = data.get("output", "(empty)")
    captured = data.get("captured_at", "")[:19].replace("T", " ")

    if HAS_RICH:
        console = Console()
        console.print(Rule(f"[bold yellow]{phase}[/bold yellow]"))
        console.print(f"[dim]Captured: {captured} | Model: {data.get('model', 'gemini-3.8-flash')}[/dim]\n")
        console.print(Panel(
            output,
            title=f"[green]{agent_name.replace('_', ' ').title()} Agent[/green]",
            border_style="green",
            expand=False,
        ))
        console.print()
    else:
        print(f"\n{'='*60}\n{phase}\n{'='*60}")
        print(f"Captured: {captured}\n")
        print(output)
        print(f"\n{'-'*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Show pre-saved ResilienceOps AI demo outputs")
    parser.add_argument("--agent", type=str, help="Show a specific agent")
    parser.add_argument("--list", action="store_true", help="List all saved outputs")
    args = parser.parse_args()

    if args.list:
        print("\nSaved demo outputs:")
        for name in DEMO_SEQUENCE:
            path = os.path.join(OUTPUT_DIR, f"{name}.json")
            status = "✓" if os.path.exists(path) else "✗ missing"
            data = load(name)
            ts = data.get("captured_at", "")[:19] if data else ""
            print(f"  {status}  {name:<22} {ts}")
        return

    if args.agent:
        show(args.agent)
    else:
        for name in DEMO_SEQUENCE:
            show(name)


if __name__ == "__main__":
    main()
