import pyautogui
import time


# Typewrite with a delay between each character
# pyautogui.typewrite('Hello, World!', interval=0.5)  # Type 'Hello, World!' with a 0.1 second delay between each character

# Hotkeys
# pyautogui.hotkey('ctrl', 'c')  # Press Ctrl+S to save

# Single Press Keys
# pyautogui.press('enter')  # Press the Enter key

# Hold keys
# pyautogui.keyDown('shift')  # Hold down the Shift key
# pyautogui.typewrite('abs')  # Press the 'a' key while Shift is
# pyautogui.keyUp('shift')  # Release the Shift key

# Screenshot
screenshot = pyautogui.screenshot()
screenshot.save('screenshot.png')  # Save the screenshot to a file