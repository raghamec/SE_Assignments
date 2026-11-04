import playwright.sync_api as playwright
import datetime as datetime

#Develop a Playwright-based WhatsApp Web automation bot to send personalized messages to multiple contacts and extract relevant information from chats.
with playwright.sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Launch browser in non-headless mode
    page = browser.new_page()
    page.goto("https://web.whatsapp.com/")
    page.wait_for_load_state("networkidle")  # Wait for the page to load completely

    # Add your automation logic here, such as sending messages or extracting information from chats.
    # Send Hi to a contact Raghav (You)
    # page.fill("input[title='Search or start new chat']", "Raghav Jio(You)")
    # page.wait_for_selector("span[title='Raghav (You)']")
    page.click("span[title='Raghav (You)']")
    page.fill("div[contenteditable='true']", "Hi")
    page.keyboard.press("Enter")


    screenshot = page.screenshot(path="screenshot_whatsapp.png")
    browser.close()