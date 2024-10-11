import os
from pathlib import Path

# create a folder to store the generated code
OUT_DIR = Path("out")

if not OUT_DIR.exists():
    OUT_DIR.mkdir()
    # initialise the folder as a git repo
    os.system(f"cd {OUT_DIR} && git init")
