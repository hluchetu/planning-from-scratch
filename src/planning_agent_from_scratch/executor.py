from __future__ import annotations

from sophons.agents import Agent

from .state import PlanState


def execute_step(state: PlanState, agent: Agent) -> str:
    past_context = ""
    if state.past_steps:
        lines = [f"- {s}: {o}" for s, o in state.past_steps]
        past_context = "\nCompleted steps so far:\n" + "\n".join(lines)

    task = (
        f"Objective: {state.objective}{past_context}\n\n"
        f"Current step to execute: {state.plan[0]}\n\n"
        "Complete only this step. Use tools if they help."
    )

    return agent(task).message
