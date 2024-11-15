import typer
import subprocess
from pathlib import Path
import shutil
from agent.logging import logger


def delete_entire_dir(dir: Path | str) -> None:
    """Delete all files and folders in a directory

    :param dir: The directory to delete
    :type dir: Path | str
    """
    shutil.rmtree(Path(dir), ignore_errors=True)


def check_for_node():
    """Checks if node.js in installed on the system"""
    try:
        logger.info("Checking that Node.js is installed.")
        version = subprocess.check_output("node --version", shell=True)
        if version:
            logger.info(f"Found node version: {version.decode().strip()}")

        return version.decode().strip()
    except Exception as e:
        logger.error(
            f"Could not find Node.js installation. Please install it from https://nodejs.org : {e}"
        )
        raise typer.Exit()


def check_for_npm():
    """Checks if npm is installed on the system"""
    try:
        logger.info("Checking that npm is installed.")
        version = subprocess.check_output("npm --version", shell=True)
        if version:
            logger.info(f"Found npm version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def check_for_playwright():
    """Checks if playwright is installed on the system"""
    try:
        logger.info("Checking that Playwright is installed.")
        version = subprocess.check_output("npx playwright --version", shell=True)
        if version:
            logger.info(f"Found playwright version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def check_for_cypress():
    """Checks if cypress is installed on the system"""
    try:
        logger.info("Checking that Cypress is installed.")
        version = subprocess.check_output("cypress --version", shell=True)
        if version:
            logger.info(f"Found cypress version: {version.decode().strip()}")

        return version.decode().strip()
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def scaffold_playwright(
    test_dir: Path | str,
    language: str,
    clean=True,
) -> None:
    """Scaffolds a playwright test environment

    :param test_dir: Path to the test directory
    :type test_dir: Path
    :param language: The language to scaffold the test environment in (python, typescript or javascript)
    :type language: str
    :param clean: Whether to clean out the test directory before scaffolding, defaults to True
    :type clean: bool, optional
    """
    # ensure test_dir is a Path object
    test_dir = Path(test_dir)

    # clean out the test directory
    if clean:
        delete_entire_dir(test_dir)

    # create the test directory
    test_dir.mkdir(exist_ok=True)

    # nothing to do for python
    if language == "python":
        return None

    # run the playwright init command
    logger.info("Running the playwright install command.")
    lang = "Typescript" if language == "typescript" else "js"
    cmd = f"npm init playwright@latest -- --yes --quiet --install-deps --no-examples --browser=chromium --lang={lang} ."

    subprocess.run(
        cmd,
        cwd=test_dir,
        shell=True,
    )

    logger.info("Adding dev dependencies.")
    subprocess.run(
        "npm install uuid --save-dev",
        cwd=test_dir,
        shell=True,
    )


def check_for_playwright_browsers(
    test_dir: Path,
):
    """Checks if playwright browsers are installed on the system"""
    try:
        logger.info("Checking that Playwright browsers are installed.")
        subprocess.run(
            "npx playwright install chromium",
            check=True,
            cwd=test_dir,
            shell=True,
        )
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False
    return True


def check_for_cypress_installation(test_dir: Path):
    """Checks if cypress is installed on the system"""
    try:
        logger.info("Checking that Cypress is installed.")
        subprocess.run(
            "npx --yes cypress install",
            check=True,
            cwd=test_dir,
            shell=True,
        )
    except subprocess.CalledProcessError:
        return False
    except OSError:
        return False


def scaffold_cypress(test_dir: Path, language: str, clean=True) -> None:
    """Scaffolds a playwright test environment

    :param test_dir: Path to the test directory
    :type test_dir: Path
    :param language: The language to scaffold the test environment in (python, typescript or javascript)
    :type language: str
    :param clean: Whether to clean out the test directory before scaffolding, defaults to True
    :type clean: bool, optional
    """

    # ensure test_dir is a Path object
    test_dir = Path(test_dir)

    # clean out the test directory
    if clean:
        delete_entire_dir(test_dir)

    # create the test directory
    test_dir.mkdir(exist_ok=True)
    # create e2e folder
    e2e_folder = test_dir / "e2e"
    e2e_folder.mkdir(exist_ok=True)
    # create a support folder
    support_folder = test_dir / "support"
    support_folder.mkdir(exist_ok=True)
    # create a fixtures folder
    fixtures_folder = test_dir / "fixtures"
    fixtures_folder.mkdir(exist_ok=True)

    # nothing to do for python
    if language == "python":
        return None

    # add a gitignore file
    logger.info("Adding a .gitignore file.")
    with open(test_dir / ".gitignore", "w") as f:
        f.write(
            """
node_modules/
.cypress/
            """
        )

    if language == "typescript":
        logger.info("Adding a support/commands.ts file.")
        with open(support_folder / "commands.ts", "w") as f:
            f.write("""""")

        logger.info("Adding a support/e2e.ts file.")
        with open(support_folder / "e2e.ts", "w") as f:
            f.write("""import './commands'

Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from
  // failing the test
  return false
})""")

        # create a package.json file
        with open(test_dir / "package.json", "w") as f:
            f.write("""{
  "name": "agent-tests",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "cypress": "latest",
    "uuid": "latest",
    "typescript": "latest"
  }
}""")

        logger.info("Adding a cypress.config.ts file.")
        with open(test_dir / "cypress.config.ts", "w") as f:
            f.write(
                """import { defineConfig } from 'cypress'

export default defineConfig({
  defaultCommandTimeout: 10000,
  e2e: {
    supportFile: "cypress/support/e2e.ts",
  },
})
"""
            )

        logger.info("Adding a tsconfig.json file.")
        with open(test_dir / "tsconfig.json", "w") as f:
            f.write(
                """{
  "compilerOptions": {
    "target": "es5",
    "lib": ["es5", "dom"],
    "types": ["cypress", "node"]
  },
  "include": ["**/*.ts"]
}
"""
            )

    if language == "javascript":
        logger.info("Adding a support/commands.js file.")
        with open(support_folder / "commands.js", "w") as f:
            f.write("""""")

        with open(support_folder / "e2e.js", "w") as f:
            f.write("""import './commands'

Cypress.on('uncaught:exception', (err, runnable) => {
  // returning false here prevents Cypress from
  // failing the test
  return false
})""")

        logger.info("Adding a cypress.config.js file.")
        with open(test_dir / "cypress.config.js", "w") as f:
            f.write(
                """const { defineConfig } = require('cypress')

module.exports = defineConfig({
  defaultCommandTimeout: 10000,
  e2e: {
    supportFile: "cypress/support/e2e.js",
  },
})
"""
            )

        logger.info("Setting up cypress environment.")
        # create a package.json file
        with open(test_dir / "package.json", "w") as f:
            f.write("""{
  "name": "agent-tests",
  "version": "1.0.0",
  "main": "index.js",
  "scripts": {
  },
  "keywords": [],
  "author": "",
  "license": "ISC",
  "devDependencies": {
    "cypress": "latest",
    "uuid": "latest",
    "typescript": "latest"
  }
}""")

    logger.info("Installing npm dependencies.")
    subprocess.run(
        "npm install",
        cwd=test_dir,
        shell=True,
    )
