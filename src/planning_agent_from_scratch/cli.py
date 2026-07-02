from __future__ import annotations

import argparse
from pathlib import Path

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.text import Text

from sophons.agents.hooks import AfterModelCall

from .main import run_plan

console = Console()

_PROMPT_STYLE = Style.from_dict({"prompt": "bold #5f87ff"})
_HISTORY_FILE = Path.home() / ".planning_agent_history"


def _print_header(thinking: bool) -> None:
    suffix = "  [dim cyan]--thinking[/dim cyan]" if thinking else ""
    console.print()
    console.print(
        Panel.fit(
            f"[bold white]Planning Agent[/bold white]  [dim]deepseek-reasoner[/dim]{suffix}\n"
            "[dim]Type your goal and press Enter. [bold]exit[/bold] or Ctrl+C to quit.[/dim]",
            border_style="bright_black",
            padding=(0, 2),
        )
    )
    console.print()


def _print_user(text: str) -> None:
    console.print(
        Panel(
            Text(text, style="white"),
            title="[bold #5f87ff]You[/bold #5f87ff]",
            border_style="#5f87ff",
            padding=(0, 1),
        )
    )


def _print_plan(steps: list[str]) -> None:
    lines = "\n".join(f"{i + 1}. {s}" for i, s in enumerate(steps))
    console.print(
        Panel(
            lines,
            title="[bold cyan]Plan[/bold cyan]",
            border_style="cyan",
            padding=(0, 1),
        )
    )


def _print_step_start(step: str) -> None:
    console.print(f"\n  [dim]⟳ executing:[/dim] [bold cyan]{step}[/bold cyan]")


def _print_step_done(step: str, observation: str) -> None:
    console.print(
        Panel(
            observation,
            title="[bold yellow]Observation[/bold yellow]",
            border_style="#facc15",
            padding=(0, 1),
        )
    )


def _print_response(text: str, steps_taken: int) -> None:
    console.print(
        Panel(
            Markdown(text),
            title="[bold #2dba4e]Agent[/bold #2dba4e]",
            subtitle=f"[dim]steps={steps_taken}[/dim]",
            border_style="#2dba4e",
            padding=(0, 1),
        )
    )


def _on_after_model(event: AfterModelCall) -> None:
    reasoning = event.message.metadata.get("reasoning")
    if reasoning:
        console.print(Panel(
            reasoning,
            title="[bold magenta]Thinking[/bold magenta]",
            border_style="magenta",
            padding=(0, 1),
        ))


def main() -> None:
    parser = argparse.ArgumentParser(prog="planning-chat", description="Planning agent CLI")
    parser.add_argument("--thinking", action="store_true", help="Show model reasoning")
    args = parser.parse_args()

    _print_header(args.thinking)

    session: PromptSession = PromptSession(
        history=FileHistory(str(_HISTORY_FILE)),
        style=_PROMPT_STYLE,
    )

    while True:
        try:
            user_input = session.prompt("  You › ", style=_PROMPT_STYLE).strip()
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted.[/dim]")
            break
        except EOFError:
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit", "/exit", "/quit"}:
            console.print("[dim]Goodbye.[/dim]")
            break

        console.print()
        _print_user(user_input)
        console.print()

        plan_ref: list[list[str]] = [[]]

        try:
            with console.status("[dim]Planning...[/dim]", spinner="dots"):
                state = run_plan(
                    objective=user_input,
                    on_plan_created=lambda steps: (_print_plan(steps), plan_ref[0].__iadd__(steps)),
                    on_step_start=_print_step_start,
                    on_step_done=_print_step_done,
                    on_after_model=_on_after_model if args.thinking else None,
                )

            console.print()
            _print_response(state.response or "", len(state.past_steps))
            console.print()

        except KeyboardInterrupt:
            console.print("\n[dim]Cancelled.[/dim]\n")
        except Exception as exc:
            console.print(f"\n[bold red]Error:[/bold red] {exc}\n")
