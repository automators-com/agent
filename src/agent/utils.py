import io
import base64
import os
import pytest
import pytest_playwright
from pathlib import Path
from contextlib import redirect_stdout
from agent.config import get_test_dir
from agent.logging import logger
from agent.video import extract_frames, keep_unique_images
import subprocess


def strip_code_fences(code):
    potential_fences = [
        "```python",
        "```py",
        "```typescript",
        "```ts",
        "```javascript",
        "```js",
        "```",
    ]
    for fence in potential_fences:
        code = code.replace(fence, "")

    return code


def run_pytest_playwright(test_dir: Path) -> str:
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


def run_playwright(test_dir: Path) -> str:
    # ensure test_dir exists
    test_dir.mkdir(exist_ok=True)
    # Create a StringIO buffer to capture the output
    buffer = io.StringIO()

    cmd = ["npx", "playwright", "test", "--trace=on", "--reporter=line"]

    # Run the command using subprocess and capture the output
    process = subprocess.Popen(
        cmd, cwd=test_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    # Write the output to the buffer
    buffer.write(stdout)
    buffer.write(stderr)

    # Get the content of the buffer
    output = buffer.getvalue()
    # Close the buffer
    buffer.close()
    return output


def run_cypress(test_dir: Path, config_file_name: str) -> str:
    # Create a StringIO buffer to capture the output
    buffer = io.StringIO()
    cmd = [
        "npx",
        "cypress",
        "run",
        "--headless",
        "--config-file",
        str(test_dir / config_file_name),
    ]

    # Run the command using subprocess and capture the output
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()

    # Write the output to the buffer
    buffer.write(stdout)
    buffer.write(stderr)

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
    test_dir = get_test_dir()

    if not test_dir:
        return screenshots

    # unzip any trace.zip folders
    trace_files = list(test_dir.glob("**/*.zip"))
    logger.info(f"Found {len(trace_files)} trace file(s).")
    if trace_files:
        for trace_file in trace_files:
            # extract the contents of the zip file
            try:
                subprocess.run(
                    f"unzip {str(trace_file)} -d {str(trace_file.parent)}",
                    shell=True,
                )
                # find all image files in any subdirectories
                keep_unique_images(test_dir)
            except Exception as e:
                logger.error(f"Error extracting trace file: {e}")

    # check for video files
    video_files = list(test_dir.glob("**/*.webm"))
    logger.info(f"Found {len(video_files)} video(s).")
    if video_files:
        for video_file in video_files:
            # extract frames from the video using moviepy
            extract_frames(video_file)

    logger.info("Checking for screenshots.")

    image_files = list(test_dir.glob("**/*.png"))

    for format in ["jpeg", "jpg", "webp"]:
        image_files.extend(list(test_dir.glob(f"**/*.{format}")))

    logger.info(f"Found {len(image_files)} screenshot(s).")
    if image_files:
        for image_file in image_files:
            # convert to base64 and display in a panel
            image_data = encode_image(image_file)
            screenshots.append(image_data)

    return screenshots
