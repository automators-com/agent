import os
import importlib.metadata
from pathlib import Path
from dotenv import load_dotenv

__app_name__ = "agent"
__version__ = importlib.metadata.version("automators-agent")

dotenv_path = Path(os.getcwd()) / ".env"
load_dotenv(dotenv_path=dotenv_path, override=True)
