import pytest
from pathlib import Path
from agent.scaffold import scaffold_cypress, delete_entire_dir


@pytest.mark.parametrize("language", ["typescript", "javascript"])
def test_cypress_scaffolding(language: str):
    test_dir = Path(f"test_cypress_{language}")

    scaffold_cypress(
        test_dir=test_dir,
        language=language,
        clean=True,
    )

    files_in_test_dir = list(test_dir.glob("*"))

    # check for the node_modules folder
    node_modules = test_dir / "node_modules"
    assert node_modules.exists()
    # check for relevant files
    assert any("package.json" in str(f) for f in files_in_test_dir)
    assert any(".gitignore" in str(f) for f in files_in_test_dir)

    if language == "javascript":
        assert any("cypress.config.js" in str(f) for f in files_in_test_dir)

    if language == "typescript":
        assert any("tsconfig.json" in str(f) for f in files_in_test_dir)
        assert any("cypress.config.ts" in str(f) for f in files_in_test_dir)

    # delete the test directory
    delete_entire_dir(test_dir)
