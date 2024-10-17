import io
import pytest
from pathlib import Path
from contextlib import redirect_stdout


def strip_code_fences(code):
    return code.replace("```python", "").replace("```", "")


def run_pytest_and_capture_output(test_dir: Path) -> str:
    # Create a StringIO buffer to capture the output
    buffer = io.StringIO()
    # Redirect the stdout to the buffer
    with redirect_stdout(buffer):
        pytest.main(["-x", str(test_dir)])
    # Get the content of the buffer
    output = buffer.getvalue()
    # Close the buffer
    buffer.close()
    return output
