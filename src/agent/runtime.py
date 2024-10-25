import subprocess
from pathlib import Path
from agent.logging import logger


def check_for_node():
    """Checks if node.js in installed on the system"""
    try:
        logger.info("Checking that Node.js is installed.")
        version = subprocess.check_output(["node", "-v"])
        if version:
            logger.info(f"found node version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def check_for_npm():
    """Checks if npm is installed on the system"""
    try:
        logger.info("Checking that npm is installed.")
        version = subprocess.check_output(["npm", "-v"])
        if version:
            logger.info(f"found npm version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def check_for_playwright():
    """Checks if playwright is installed on the system"""
    try:
        logger.info("Checking that Playwright is installed.")
        version = subprocess.check_output(["playwright", "--version"])
        if version:
            logger.info(f"found playwright version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def setup_playwright_env(test_dir: Path, language: str):
    # run the playwright init command
    logger.info("Running the playwright install command.")
    subprocess.run(
        [
            "npm",
            "init",
            "playwright",
            "--",
            "--quiet",
            "--install-deps",
            "--no-examples",
            "--browser=chromium",
            f"--lang={"Typescript" if language == "typescript" else "js"}",
            ".",
        ],
        cwd=test_dir,
    )

    logger.info("Adding dev dependencies.")
    subprocess.run(
        ["npm", "install", "uuid", "--save-dev"],
        cwd=test_dir,
    )


def check_for_playwright_browsers(
    test_dir: Path,
):
    """Checks if playwright browsers are installed on the system"""
    try:
        logger.info("Checking that Playwright browsers are installed.")
        subprocess.run(
            ["playwright", "install", "chromium"],
            check=True,
            cwd=test_dir,
        )
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False
    return True
