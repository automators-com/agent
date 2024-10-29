import pytest
from pathlib import Path
from agent.scaffold import scaffold_playwright, delete_entire_dir


@pytest.mark.parametrize("language", ["python", "typescript", "javascript"])
def test_playwright_scaffolding(language: str):
    test_dir = Path(f"test_playwright_{language}")

    scaffold_playwright(
        test_dir=test_dir,
        language=language,
        clean=True,
    )

    files_in_test_dir = list(test_dir.glob("*"))

    # check for the node_modules folder
    node_modules = test_dir / "node_modules"

    if language != "python":
        # check for the node_modules folder
        assert node_modules.exists()

        # check for relevant files
        assert any("package.json" in str(f) for f in files_in_test_dir)
        assert any(".gitignore" in str(f) for f in files_in_test_dir)

    if language == "javascript":
        assert any("playwright.config.js" in str(f) for f in files_in_test_dir)

    if language == "typescript":
        assert any("playwright.config.ts" in str(f) for f in files_in_test_dir)

    # delete the test directory
    delete_entire_dir(test_dir)
