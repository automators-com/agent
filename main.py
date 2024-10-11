import os
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

from src.completions import generate_test_code
from src.setup import OUT_DIR
from src.utils import strip_code_fences

load_dotenv()

url = "https://dev.datamaker.app"


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=os.environ.get("HEADLESS") == "true")
        page = browser.new_page()
        page.goto(url)
        content = page.content()

        # Test Generation
        prompt = "Write some headless python playwright tests for the user signup."
        completion = generate_test_code(content, prompt, url)
        code = completion.choices[0].message.content

        # write code to file
        # TODO: Determine file name
        with open(OUT_DIR / "test_datamaker.py", "w+") as f:
            f.write(strip_code_fences(code))

        # run the pytest command in the out directory
        os.system(f"cd {OUT_DIR} && pytest")
        browser.close()


if __name__ == "__main__":
    main()
