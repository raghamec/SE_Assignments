import pyautogui
import time

pyautogui.FAILSAFE = True
pyautogui.PAUSE = 1.0

pyautogui.moveTo(100, 100, duration=5)  # Move the mouse to (100, 100) over 1 second
time.sleep(1)  # Wait for 1 second
pyautogui.click(100,25)  # Click the mouse at the current position
pyautogui.moveTo(500,500, duration=5)  # Move the mouse to (200, 200) over 1 second
pyautogui.scroll(500)  # Scroll up 500 units
pyautogui.scroll(-500)  # Scroll down 500 units
