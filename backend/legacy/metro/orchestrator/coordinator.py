from __future__ import annotations

import asyncio
import time
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from agents import ALL_AGENTS

PHASE_TO_AGENTS = {
    "forecast_and_prepare": ["sentinel", "risk_memory", "preparedness"],
    "live_response": ["triage", "field_intel", "dispatch", "communication"],
    "recover_and_improve": ["damage_assessment", "reconciliation", "preparedness"],
}


class ResilienceOpsCoordinator:
    """
    Manages ADK Runner instances for all 9 ResilienceOps agents.
    Each run_agent call gets its own async context + session so there are
    no event-loop conflicts between sequential agent calls.
    """

    def __init__(self, app_name: str = "resilience_ops_ai"):
        self.app_name = app_name

    async def _run_agent_async(self, agent_name: str, prompt: str) -> str:
        if agent_name not in ALL_AGENTS:
            return f"Unknown agent: {agent_name}. Available: {list(ALL_AGENTS.keys())}"

        session_service = InMemorySessionService()
        session = await session_service.create_session(
            app_name=self.app_name,
            user_id=f"eoc_{agent_name}",
        )

        runner = Runner(
            agent=ALL_AGENTS[agent_name],
            app_name=self.app_name,
            session_service=session_service,
        )

        message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)],
        )

        response_parts = []
        async for event in runner.run_async(
            user_id=f"eoc_{agent_name}",
            session_id=session.id,
            new_message=message,
        ):
            if event.is_final_response():
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if hasattr(part, "text") and part.text:
                            response_parts.append(part.text)

        return "\n".join(response_parts) if response_parts else "(No response)"

    def run_agent(self, agent_name: str, prompt: str, retries: int = 3) -> str:
        for attempt in range(retries):
            try:
                return asyncio.run(self._run_agent_async(agent_name, prompt))
            except Exception as e:
                err = str(e)
                if "503" in err or "UNAVAILABLE" in err:
                    wait = 2 ** attempt
                    print(f"  [Model busy, retrying in {wait}s... attempt {attempt+1}/{retries}]")
                    time.sleep(wait)
                elif "429" in err or "RESOURCE_EXHAUSTED" in err:
                    wait = 30 * (attempt + 1)
                    print(f"  [Rate limit hit, waiting {wait}s... attempt {attempt+1}/{retries}]")
                    time.sleep(wait)
                else:
                    raise
        return "(Model unavailable after retries — please try again shortly)"

    def run_phase(self, phase: str, prompt: str) -> dict[str, str]:
        agent_names = PHASE_TO_AGENTS.get(phase, [])
        if not agent_names:
            return {"error": f"Unknown phase '{phase}'. Valid: {list(PHASE_TO_AGENTS.keys())}"}
        return {name: self.run_agent(name, prompt) for name in agent_names}
