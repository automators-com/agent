import logging
import os
from rich.logging import RichHandler
from dotenv import load_dotenv

load_dotenv()

FORMAT = "%(message)s"
logging.basicConfig(
    level=os.environ.get("LOG_LEVEL", "INFO"),
    format=FORMAT,
    datefmt="[%X]",
    handlers=[RichHandler()],
)

logger = logging.getLogger("agent")
