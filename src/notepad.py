"""Notepad automation workflow."""

from __future__ import annotations

import time
from pathlib import Path

from . import mouse_keyboard as mk
from . import screenshot
from .config import get_config
from .ocr_grounder import ground_icon, GroundingError


def wait_for_notepad(timeout: float = 5.0) -> bool:
    """
    Wait for Notepad window to appear.
    Uses a simple time-based wait since we removed pywin32.
    
    Args:
        timeout: Time to wait in seconds
        
    Returns:
        True (assumes window appeared after wait)
    """
    time.sleep(min(timeout, 2.0))
    return True


def launch_notepad_from_desktop() -> None:
    """
    Launch Notepad by finding and double-clicking its desktop icon.
    
    Raises:
        GroundingError: If Notepad icon cannot be found after retries
    """
    config = get_config()
    
    # Show the desktop
    print("  Showing desktop...")
    mk.show_desktop()
    time.sleep(0.5)
    
    last_error = None
    
    for attempt in range(config.max_retries):
        try:
            # Capture screenshot
            screenshot_path = screenshot.capture_desktop(
                config.screenshots_dir,
                f"desktop_attempt_{attempt + 1}.png"
            )
            print(f"  Screenshot: {screenshot_path}")
            
            # Ground the Notepad icon
            result = ground_icon(screenshot_path, "Notepad")
            
            print(f"  Clicking at ({result.x}, {result.y})...")
            mk.double_click(result.x, result.y)
            
            # Wait for Notepad to launch
            print("  Waiting for Notepad...")
            wait_for_notepad()
            print("  ✓ Notepad launched!")
            return
                
        except GroundingError as e:
            last_error = e
            wait_time = config.retry_delay * (2 ** attempt)  # Exponential backoff
            print(f"  Attempt {attempt + 1} failed: {e}")
            
            if attempt < config.max_retries - 1:
                print(f"  Retrying in {wait_time:.1f}s...")
                time.sleep(wait_time)
    
    # All retries failed
    raise last_error or GroundingError("Failed to launch Notepad after all retries")


def type_content(text: str) -> None:
    """Type content into the active Notepad window."""
    time.sleep(0.3)
    mk.type_text(text)


def save_file(filepath: Path) -> None:
    """Save the current Notepad content to a file."""
    filepath = Path(filepath)
    filepath.parent.mkdir(parents=True, exist_ok=True)
    
    # Ctrl+S to save
    mk.hotkey('ctrl', 's')
    time.sleep(0.5)
    
    # Type the filepath
    mk.type_text(str(filepath))
    time.sleep(0.2)
    
    # Press Enter to confirm
    mk.press('enter')
    time.sleep(0.3)
    
    # Handle "file exists" dialog
    mk.press('left')
    mk.press('enter')
    time.sleep(0.2)


def close_notepad() -> None:
    """Close the current Notepad window."""
    mk.hotkey('alt', 'F4')
    time.sleep(0.3)
    mk.press('n')  # Don't save if prompted
    time.sleep(0.2)


def process_post(post_id: int, title: str, body: str, output_dir: Path) -> Path:
    """
    Type a post into Notepad and save it.
    
    Returns:
        Path to the saved file
    """
    content = f"Title: {title}\n\n{body}"
    type_content(content)
    
    filepath = output_dir / f"post_{post_id}.txt"
    save_file(filepath)
    
    return filepath
