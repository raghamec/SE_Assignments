import pyautogui
import time
import pyperclip
import re
import datetime
import os
from openpyxl import Workbook, load_workbook


pyautogui.FAILSAFE = True
time.sleep(2)  # Give some time to move the mouse to the fail-safe position

# Step-1 Open the chrome
pyautogui.hotkey('win', 'r')  # Open the Run dialog
time.sleep(1)  # Wait for the Run dialog to open
pyautogui.typewrite('chrome')  # Type 'chrome' in the Run dialog
pyautogui.press('enter')  # Press the Enter key to execute the command
time.sleep(5)  # Wait for Chrome to open

# pyautogui.hotkey('ctrl', 't')  # Open a new tab in Chrome
# time.sleep(2)  # Wait for the new tab to open

# Step-2 Open the Stockmarket website

pyautogui.write('https://www.nseindia.com/market-data/live-market-indices')
pyautogui.press('enter')

time.sleep(5)  # Wait for the webpage to load

# Copy webpage text
pyautogui.hotkey('ctrl', 'a')
pyautogui.hotkey('ctrl', 'c')

time.sleep(2)

text = pyperclip.paste()

# Extract only current NIFTY 50 value
match = re.search(
    r'NIFTY 50\s+([\d,]+\.\d+)',
    text,
    re.IGNORECASE
)

if match:

    nifty_value = float(match.group(1).replace(',', ''))

    # Current date and time
    current_time = datetime.datetime.now()

    # Excel file
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    filename = f"daily_report_{today}.xlsx"

    # Create or open workbook
    if os.path.exists(filename):
        wb = load_workbook(filename)
        ws = wb.active
    else:
        wb = Workbook()
        ws = wb.active
        ws.append(["Date", "Time", "NIFTY 50","Comment"])

    # Determine market comment
    if nifty_value > 24000:
        market_comment = "Bull Market"
    else:
        market_comment = "Bear Market"

    # Add new row
    ws.append([
        current_time.strftime("%d-%m-%Y"),
        current_time.strftime("%H:%M:%S"),
        nifty_value,
        market_comment
    ])

    # Save Excel
    wb.save(filename)

    print("NIFTY 50:", nifty_value)
    print("Market Status:", market_comment)
    print("Excel updated successfully!")

else:
    print("NIFTY 50 value not found. Check NSE webpage.")


# Open Excel using Windows Run (Win + R)
pyautogui.hotkey('win', 'r')
time.sleep(2)

pyautogui.write('excel', interval=0.1)
pyautogui.press('enter')

time.sleep(5)

# Open saved Excel report
pyautogui.hotkey('ctrl', 'o')
time.sleep(2)

pyautogui.write(os.path.abspath(filename), interval=0.03)
pyautogui.press('enter')

# Wait for Excel file to load
time.sleep(5)

# Maximize Excel window
pyautogui.hotkey('win', 'up')
time.sleep(2)

# Take screenshot of Excel
today = datetime.datetime.now().strftime("%Y-%m-%d")

screenshot_file = f"nifty50_screenshot_{today}.png"

pyautogui.screenshot().save(screenshot_file)

print("Excel screenshot saved:", screenshot_file)
