import io
import base64
import os
import pytest
import pytest_playwright
from pathlib import Path
from contextlib import redirect_stdout
from agent.logging import logger
from agent.video import extract_frames


def strip_code_fences(code):
    return code.replace("```python", "").replace("```", "")


def run_pytest_and_capture_output(test_dir: Path) -> str:
    # Create a StringIO buffer to capture the output
    buffer = io.StringIO()
    args = [
        "-v",
        str(test_dir),
        "--screenshot=on",
        "--video=on",
        "--full-page-screenshot",
    ]

    headless = os.environ.get("HEADLESS", False)
    if not headless:
        args.append("--headed")

    # Redirect the stdout to the buffer
    with redirect_stdout(buffer):
        pytest.main(
            args,
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
        # check for video files
        video_files = list(test_results.glob("**/*.webm"))
        logger.info(f"Found {len(video_files)} video(s).")

        if video_files:
            for video_file in video_files:
                # extract frames from the video using moviepy
                extract_frames(video_file)

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
