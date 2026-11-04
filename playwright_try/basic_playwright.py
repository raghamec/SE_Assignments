import playwright.sync_api as playwright

with playwright.sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto("https://www.google.com")
    screenshot = page.screenshot(path="screenshot_playwright.png")
    browser.close()