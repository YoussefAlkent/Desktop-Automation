"""Screenshot capture utilities."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import mss
import mss.tools


def capture_desktop(output_dir: Optional[Path] = None, filename: Optional[str] = None) -> Path:
    """
    Capture a screenshot of the entire desktop.
    
    Args:
        output_dir: Directory to save screenshot (default: cwd/screenshots)
        filename: Custom filename (default: timestamp-based)
        
    Returns:
        Path to the saved screenshot
    """
    if output_dir is None:
        output_dir = Path.cwd() / "screenshots"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if filename is None:
        filename = f"desktop_{int(time.time() * 1000)}.png"
    
    output_path = output_dir / filename
    
    with mss.mss() as sct:
        # Capture primary monitor
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)
        mss.tools.to_png(screenshot.rgb, screenshot.size, output=str(output_path))
    
    return output_path


def get_screen_size() -> tuple[int, int]:
    """Get the primary monitor resolution."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        return monitor["width"], monitor["height"]
