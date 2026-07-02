from __future__ import annotations

from collections.abc import Callable

from sophons.agents.hooks import HookRegistry
from sophons.integrations.models import DeepSeekModel
from sophons.integrations.tools import tavily_web_search

from .config import settings
from .loop import run
from .state import PlanState


def _build_models() -> tuple[DeepSeekModel, DeepSeekModel]:
    planner = DeepSeekModel(
        model="deepseek-reasoner",
        api_key=settings.deepseek_api_key,
        thinking=True,
    )
    executor = DeepSeekModel(
        model="deepseek-reasoner",
        api_key=settings.deepseek_api_key,
        thinking=True,
    )
    return planner, executor


def run_plan(
    objective: str,
    hooks: HookRegistry | None = None,
    on_plan_created: Callable[[list[str]], None] | None = None,
    on_step_start: Callable[[str], None] | None = None,
    on_step_done: Callable[[str, str], None] | None = None,
) -> PlanState:
    planner, executor = _build_models()
    tools = [tavily_web_search(api_key=settings.tavily_api_key)]

    return run(
        objective=objective,
        planner_model=planner,
        executor_model=executor,
        tools=tools,
        hooks=hooks,
        on_plan_created=on_plan_created,
        on_step_start=on_step_start,
        on_step_done=on_step_done,
    )
