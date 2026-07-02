from __future__ import annotations

import datetime

from sophons.agents import Agent
from sophons.agents.hooks import HookRegistry
from sophons.agents.session import InMemorySessionManager
from sophons.integrations.models import DeepSeekModel
from sophons.tools.base import Tool

from .prompts import build_executor_prompt
from .state import PlanState


def execute_step(
    state: PlanState,
    model: DeepSeekModel,
    tools: list[Tool],
    hooks: HookRegistry | None = None,
) -> str:
    step = state.plan[0]
    today = datetime.date.today().isoformat()

    past_context = ""
    if state.past_steps:
        lines = [f"- {s}: {o}" for s, o in state.past_steps]
        past_context = "\nCompleted steps so far:\n" + "\n".join(lines)

    task = (
        f"Objective: {state.objective}{past_context}\n\n"
        f"Current step to execute: {step}\n\n"
        "Complete only this step. Use tools if they help."
    )

    agent = Agent(
        model=model,
        tools=tools,
        system_prompt=build_executor_prompt(today),
        session_manager=InMemorySessionManager(),
        hooks=hooks,
    )

    result = agent.run_sync(task)
    return result.message
