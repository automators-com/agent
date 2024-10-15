import os
from pathlib import Path
from agent.logging import logger

# create a folder to store the generated code
TEST_DIR = Path("tests")

if not TEST_DIR.exists():
    TEST_DIR.mkdir()
    # initialise the folder as a git repo
    os.system(f"cd {TEST_DIR} && git init")


def clean_dir():
    """Clean the tests directory"""
    logger.info(f"Deleting files in the {TEST_DIR} directory")
    os.popen(f"rm -rf {TEST_DIR}/*").read()
