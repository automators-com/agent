import json
import logging
import os
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme
from rich.panel import Panel

console = Console(
    theme=Theme(
        {
            "logging.level.info": "medium_spring_green",
            "logging.level.debug": "cadet_blue",
            "logging.level.warning": "yellow1",
            "logging.level.error": "indian_red1",
        }
    ),
)

FORMAT = "%(message)s"
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler(markup=True, console=console, rich_tracebacks=True)],
)

logger = logging.getLogger("agent")


def log_completion(res: dict):
    # try to get ai message content
    try:
        content = json.loads(res)["choices"][0]["message"]["content"]
    except KeyError:
        content = None

    # try to get tool function calls

    try:
        tool_calls = json.loads(res)["choices"][0]["message"]["tool_calls"]
    except KeyError:
        tool_calls = None

    # log info in a panel
    if content:
        console.print("\n")
        console.print(
            Panel(str(content), title="Agent Message", padding=(1, 1), highlight=True)
        )
        console.print("\n")

    if tool_calls:
        # loop through tool calls and format them as python function calls
        for tool_call in tool_calls:
            name = tool_call["function"]["name"]
            kwargs = json.loads(tool_call["function"]["arguments"])
            # truncate any long arguments
            for key, value in kwargs.items():
                if len(str(value)) > 50:
                    kwargs[key] = f"{str(value)[:50]}..."

            console.print("\n")
            console.print(
                Panel(
                    f"{name}({kwargs})",
                    title="Tool Called",
                    padding=(1, 1),
                    highlight=True,
                )
            )
            console.print("\n")
