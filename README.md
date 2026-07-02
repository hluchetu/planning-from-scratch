# Planning Agent From Scratch

A plan-and-execute agent built from scratch on top of [Sophons](https://github.com/hluchetu/sophons).

Part of the **Architecture Patterns Behind AI Agents** series — read the companion article: [Planning: The Agent Knows What It Still Has to Do](https://hluchetu.com/articles/agent-patterns-planning).

## What this is

A ReAct agent decides one step at a time with no view of what still needs to be done. For shallow tasks that is fine. For goals that require multiple coordinated steps — a research report, a debugging investigation, a competitive analysis — it wanders.

This agent adds a planning layer on top of the ReAct loop:

1. **Planner** — takes the user goal, produces an ordered task list before any tool runs
2. **Executor** — works through each step using a full ReAct loop (the Sophons `Agent`)
3. **Update loop** — after each step, decides whether to continue, replan, or stop

The plan is a living document. If a step reveals that the original assumption was wrong, the agent revises the remaining steps rather than continuing toward a now-invalid conclusion.

## Architecture

```
User goal
    │
    ▼
┌─────────┐
│ Planner │  DeepSeek Reasoner — produces an ordered task list
└────┬────┘
     │  plan = ["step 1", "step 2", ...]
     ▼
┌──────────────────────────────────────┐
│              Update Loop             │
│                                      │
│  ┌──────────┐      ┌──────────────┐  │
│  │ Executor │ ───▶ │ Update Plan  │  │
│  └──────────┘      └──────┬───────┘  │
│   ReAct loop              │          │
│   (Sophons Agent)   done? │ replan?  │
└───────────────────────────┼──────────┘
                            ▼
                       Final answer
```

**State at every point:**
- `objective` — the original user goal, never changes
- `plan` — steps still to execute
- `past_steps` — `(step, observation)` pairs already completed
- `response` — set when the loop is finished

## Models

- **Planner**: `deepseek-reasoner` — chain-of-thought reasoning for task decomposition
- **Executor**: `deepseek-reasoner` — runs each step as its own ReAct loop with tools

## Tools

Web search is provided by [Tavily](https://tavily.com) via the `sophons.integrations.tools` integration.

## Setup

```bash
git clone https://github.com/hluchetu/planning-agent-from-scratch
cd planning-agent-from-scratch
uv sync
```

Copy `.env.example` to `.env` and add your keys:

```bash
cp .env.example .env
```

```env
DEEPSEEK_API_KEY=your_key_here
TAVILY_API_KEY=your_key_here
```

## Run

```bash
uv run planning-chat
```

## How it differs from ReAct

| | ReAct | Plan and Execute |
|---|---|---|
| Before acting | Nothing | Produces a task list |
| Per step | Decides next action from last observation | Executes one planned step via ReAct |
| Progress tracking | None | `plan` and `past_steps` visible at every point |
| Best for | Shallow tasks (1–3 steps) | Complex multi-step goals |
| Overhead | Minimal | One extra model call upfront |

## Related

- [ReAct From Scratch](https://github.com/hluchetu/ReAct-from-scratch) — the agent this builds on
- [Sophons](https://github.com/hluchetu/sophons) — the agent SDK powering both
- [Architecture Patterns Behind AI Agents](https://hluchetu.com/articles/agent-patterns-intro) — the full series
