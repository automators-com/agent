import io
import base64
import pytest
import pytest_playwright
from pathlib import Path
from contextlib import redirect_stdout
from agent.logging import logger


def strip_code_fences(code):
    return code.replace("```python", "").replace("```", "")


def run_pytest_and_capture_output(test_dir: Path) -> str:
    # Create a StringIO buffer to capture the output
    buffer = io.StringIO()
    # Redirect the stdout to the buffer
    with redirect_stdout(buffer):
        pytest.main(
            ["-v", str(test_dir), "--screenshot=only-on-failure"],
            plugins=[pytest_playwright],
        )
    # Get the content of the buffer
    output = buffer.getvalue()
    # Close the buffer
    buffer.close()
    return output


# Function to encode the image
def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def check_for_screenshots():
    screenshots = []
    # check for a trace.zip file and extract it if it exists
    test_results = Path("test-results")

    if test_results.exists():
        logger.info("Test results folder found. Checking for screenshots.")
        # find all image files in any subdirectories
        image_files = list(test_results.glob("**/*.png"))
        logger.info(f"Found {len(image_files)} screenshot(s).")
        if image_files:
            for image_file in image_files:
                # convert to base64 and display in a panel
                image_data = encode_image(image_file)
                screenshots.append(image_data)

    return screenshots
