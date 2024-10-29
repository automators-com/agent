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

    node_modules = test_dir / "node_modules"
    e2e_folder = test_dir / "e2e"
    support_folder = test_dir / "support"

    # check for the node_modules folder
    assert node_modules.exists()
    # check for an e2e folder
    assert e2e_folder.exists()
    # check for support folder
    assert support_folder.exists()

    # check for relevant files
    assert any("package.json" in str(f) for f in files_in_test_dir)
    assert any(".gitignore" in str(f) for f in files_in_test_dir)

    if language == "javascript":
        assert any("cypress.config.js" in str(f) for f in files_in_test_dir)
        # check for the support/commands.js file
        commands_file = support_folder / "commands.js"
        assert commands_file.exists()

        # check for the support/e2e.js file
        e2e_file = support_folder / "e2e.js"
        assert e2e_file.exists()

    if language == "typescript":
        assert any("tsconfig.json" in str(f) for f in files_in_test_dir)
        assert any("cypress.config.ts" in str(f) for f in files_in_test_dir)

        # check for the support/commands.js file
        commands_file = support_folder / "commands.ts"
        assert commands_file.exists()

        # check for the support/e2e.js file
        e2e_file = support_folder / "e2e.ts"
        assert e2e_file.exists()

    # delete the test directory
    delete_entire_dir(test_dir)
