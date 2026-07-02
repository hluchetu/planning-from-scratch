from __future__ import annotations

import datetime
from collections.abc import Callable

from sophons.agents import Agent
from sophons.integrations.models import DeepSeekModel
from sophons.integrations.tools import tavily_web_search

from .config import settings
from .loop import run
from .prompts import build_executor_prompt
from .state import PlanState


def run_plan(
    objective: str,
    on_plan_created: Callable[[list[str]], None] | None = None,
    on_step_start: Callable[[str], None] | None = None,
    on_step_done: Callable[[str, str], None] | None = None,
    on_after_model: Callable | None = None,
) -> PlanState:
    planner = DeepSeekModel(
        model="deepseek-reasoner",
        api_key=settings.deepseek_api_key,
        thinking=True,
    )

    executor_agent = Agent(
        model=DeepSeekModel(
            model="deepseek-reasoner",
            api_key=settings.deepseek_api_key,
            thinking=True,
        ),
        tools=[tavily_web_search(api_key=settings.tavily_api_key)],
        system_prompt=build_executor_prompt(datetime.date.today().isoformat()),
    )

    if on_after_model:
        executor_agent.add_hook(on_after_model)

    return run(
        objective=objective,
        planner_model=planner,
        executor_agent=executor_agent,
        on_plan_created=on_plan_created,
        on_step_start=on_step_start,
        on_step_done=on_step_done,
    )
