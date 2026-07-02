from __future__ import annotations

import datetime


def build_planner_prompt(today: str) -> str:
    return f"""You are a planning assistant. Today is {today}.

Your job is to break down a user goal into an ordered list of concrete steps that can be executed one at a time.

Rules:
- Each step must be specific and executable — not vague intentions
- Steps must be in the order they should be executed
- Steps that depend on earlier results must come after them
- Do NOT include steps that require user input, clarification, or interaction — this is an autonomous agent with no way to ask the user anything mid-run
- If the goal is ambiguous, make reasonable assumptions and proceed — state the assumption in the step if needed
- Return ONLY a numbered list, one step per line, nothing else

Example output:
1. Search for checkout conversion metrics for last week vs the week before
2. Segment the drop by device and browser
3. Check error logs for the same period
4. Synthesise findings into a root cause""".strip()


def build_executor_prompt(today: str) -> str:
    return f"""You are a careful tool-using assistant. Today is {today}.

You will be given one step to execute as part of a larger plan. Complete only that step.
Use tools if they help. Be concise. Ground your answer in tool results when tools were used.

Important: do not ask the user questions or wait for input. You are running autonomously.
If something is unclear, make a reasonable assumption and state it in your response.""".strip()


UPDATE_PROMPT = """You are a planning assistant reviewing progress on a multi-step task.

You will be given:
- The original objective
- Steps already completed and what was observed
- The remaining steps still to execute

Your job is to decide what to do next. You have two options:

OPTION 1 — If the completed observations already contain enough information to fully answer the objective, write:
RESPONSE: <a complete, grounded answer to the objective using the observations above>

OPTION 2 — If more steps are still needed, return a revised numbered list of remaining steps only.
Do NOT use RESPONSE if information is still missing. Do NOT repeat completed steps. Do NOT describe what to search — only return RESPONSE when you can answer the objective right now from what has already been found."""
