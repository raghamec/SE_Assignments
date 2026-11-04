import playwright.sync_api as playwright
import datetime as datetime

from pyperclip import copy

with playwright.sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Launch browser in non-headless mode
    page = browser.new_page()
    page.goto("https://www.cricbuzz.com/")
    page.wait_for_load_state("networkidle")  # Wait for the page to load completely
    # element = page.query_selector("Schedule")  # Replace with the actual selector for the element you want to capture
    # copy(element.text_content())
    # print("Text copied to clipboard:", element.text_content())

    screenshot = page.screenshot(path="screenshot_cricbuzz.png")
    browser.close()