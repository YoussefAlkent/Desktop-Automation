"""Mouse and keyboard automation utilities."""

from __future__ import annotations

import time
from typing import List

import pyautogui
import pyperclip

# Safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1


def click(x: int, y: int) -> None:
    """Single click at coordinates."""
    pyautogui.click(x, y)


def double_click(x: int, y: int) -> None:
    """Double-click at coordinates."""
    pyautogui.doubleClick(x, y)


def move_to(x: int, y: int) -> None:
    """Move mouse to coordinates."""
    pyautogui.moveTo(x, y)


def type_text(text: str, use_clipboard: bool = True) -> None:
    """
    Type text into the active window.
    
    Args:
        text: Text to type
        use_clipboard: If True, use clipboard paste for reliability
    """
    if use_clipboard:
        # Use clipboard for special characters and speed
        original = pyperclip.paste()
        pyperclip.copy(text)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(0.1)
        pyperclip.copy(original)  # Restore original clipboard
    else:
        pyautogui.typewrite(text, interval=0.02)


def hotkey(*keys: str) -> None:
    """Press a keyboard shortcut."""
    pyautogui.hotkey(*keys)


def press(key: str) -> None:
    """Press a single key."""
    pyautogui.press(key)


def show_desktop() -> None:
    """Minimize all windows to show the desktop (Win+D)."""
    pyautogui.hotkey('win', 'd')
    time.sleep(0.5)
