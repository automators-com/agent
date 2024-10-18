import logging
import os
from rich.logging import RichHandler
from rich.console import Console
from rich.theme import Theme

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
