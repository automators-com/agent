import os
from pathlib import Path
from agent.logging import logger

# create a folder to store the generated code
TEST_DIR = Path("tests")


def setup():
    # create the tests directory if it doesn't exist
    TEST_DIR.mkdir(exist_ok=True)
    # install playwright browsers
    os.popen("playwright install")


def clean_dir():
    """Clean the tests directory"""
    logger.info(f"Deleting files in the {TEST_DIR} directory")
    os.popen(f"rm -rf {TEST_DIR}/*").read()
