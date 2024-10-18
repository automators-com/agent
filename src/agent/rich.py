from agent.logging import console
from rich.panel import Panel


def print_in_question_panel(text: str, title: str = "Question?"):
    console.print("\n")
    console.print(
        Panel(
            text,
            title=title,
            padding=(1, 1),
            highlight=True,
            border_style="color(49)",
        )
    )
    console.print("\n")


def print_in_panel(text: str, title: str = "Output"):
    console.print("\n")
    console.print(
        Panel(
            text,
            title=title,
            padding=(1, 1),
            highlight=True,
        )
    )
    console.print("\n")
