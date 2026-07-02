from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PlanState:
    objective: str
    plan: list[str] = field(default_factory=list)
    past_steps: list[tuple[str, str]] = field(default_factory=list)
    response: str | None = None
