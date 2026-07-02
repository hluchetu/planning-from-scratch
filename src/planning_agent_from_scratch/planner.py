from __future__ import annotations

import datetime

from sophons.integrations.models import DeepSeekModel
from sophons.models.messages import Message

from .prompts import build_planner_prompt


def create_plan(objective: str, model: DeepSeekModel) -> list[str]:
    today = datetime.date.today().isoformat()
    messages = [
        Message(role="system", content=build_planner_prompt(today)),
        Message(role="user", content=objective),
    ]
    response = model.invoke(messages)
    return _parse_plan(response.content)


def _parse_plan(text: str) -> list[str]:
    steps = []
    for line in text.strip().splitlines():
        line = line.strip()
        if not line:
            continue
        # Strip leading "1." or "1)" or "-"
        for prefix in (".)", "-"):
            parts = line.split(prefix, 1)
            if len(parts) == 2 and parts[0].strip().isdigit():
                line = parts[1].strip()
                break
        else:
            if line[0].isdigit() and len(line) > 1 and line[1] in ".)" :
                line = line[2:].strip()
        if line:
            steps.append(line)
    return steps
