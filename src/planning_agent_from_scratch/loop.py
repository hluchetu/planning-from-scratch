from __future__ import annotations

from sophons.agents.hooks import HookRegistry
from sophons.integrations.models import DeepSeekModel
from sophons.models.messages import Message
from sophons.tools.base import Tool

from .executor import execute_step
from .planner import create_plan
from .prompts import UPDATE_PROMPT
from .state import PlanState

_MAX_STEPS = 10


def _update(state: PlanState, model: DeepSeekModel) -> PlanState:
    past = "\n".join(f"- {s}: {o}" for s, o in state.past_steps)
    remaining = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(state.plan))

    content = (
        f"Objective: {state.objective}\n\n"
        f"Completed steps:\n{past}\n\n"
        f"Remaining plan:\n{remaining}"
    )

    messages = [
        Message(role="system", content=UPDATE_PROMPT),
        Message(role="user", content=content),
    ]
    response = model.invoke(messages)
    text = response.content.strip()

    if text.startswith("RESPONSE:"):
        state.response = text[len("RESPONSE:"):].strip()
    else:
        from .planner import _parse_plan
        state.plan = _parse_plan(text)

    return state


def run(
    objective: str,
    planner_model: DeepSeekModel,
    executor_model: DeepSeekModel,
    tools: list[Tool],
    hooks: HookRegistry | None = None,
    on_plan_created: object = None,
    on_step_start: object = None,
    on_step_done: object = None,
) -> PlanState:
    state = PlanState(objective=objective)
    state.plan = create_plan(objective, planner_model)

    if callable(on_plan_created):
        on_plan_created(state.plan)

    steps_taken = 0

    while state.plan and state.response is None and steps_taken < _MAX_STEPS:
        step = state.plan[0]

        if callable(on_step_start):
            on_step_start(step)

        observation = execute_step(state, executor_model, tools, hooks=hooks)
        state.past_steps.append((step, observation))
        state.plan.pop(0)
        steps_taken += 1

        if callable(on_step_done):
            on_step_done(step, observation)

        if state.plan:
            state = _update(state, planner_model)
        elif state.response is None:
            state.response = observation

    return state
