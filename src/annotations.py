"""Screenshot annotation utilities for deliverables."""

from __future__ import annotations

from pathlib import Path
from typing import Tuple

from PIL import Image, ImageDraw, ImageFont


def annotate_screenshot(
    screenshot_path: Path,
    x: int,
    y: int,
    label: str,
    output_path: Path = None,
    color: Tuple[int, int, int] = (0, 255, 0),
    radius: int = 40,
) -> Path:
    """
    Annotate a screenshot with a circle and label at the detected coordinates.
    
    Args:
        screenshot_path: Path to the original screenshot
        x, y: Coordinates of the detected icon
        label: Label text (e.g., "Notepad detected")
        output_path: Path for annotated output
        color: RGB color for annotations
        radius: Circle radius
        
    Returns:
        Path to the annotated screenshot
    """
    screenshot_path = Path(screenshot_path)
    
    if output_path is None:
        output_path = screenshot_path.parent / f"{screenshot_path.stem}_annotated{screenshot_path.suffix}"
    
    # Open and annotate
    img = Image.open(screenshot_path)
    draw = ImageDraw.Draw(img)
    
    # Draw circle
    draw.ellipse(
        [x - radius, y - radius, x + radius, y + radius],
        outline=color,
        width=3
    )
    
    # Draw crosshairs
    draw.line([(x - radius - 10, y), (x + radius + 10, y)], fill=color, width=2)
    draw.line([(x, y - radius - 10), (x, y + radius + 10)], fill=color, width=2)
    
    # Add label
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    
    label_y = y + radius + 15
    
    # Draw label with background
    bbox = draw.textbbox((x - radius, label_y), label, font=font)
    draw.rectangle([bbox[0] - 3, bbox[1] - 3, bbox[2] + 3, bbox[3] + 3], fill=(0, 0, 0))
    draw.text((x - radius, label_y), label, fill=(255, 255, 255), font=font)
    
    # Add coordinates
    coord_text = f"({x}, {y})"
    coord_y = label_y + 25
    bbox = draw.textbbox((x - radius, coord_y), coord_text, font=font)
    draw.rectangle([bbox[0] - 3, bbox[1] - 3, bbox[2] + 3, bbox[3] + 3], fill=(0, 0, 0))
    draw.text((x - radius, coord_y), coord_text, fill=(255, 255, 0), font=font)
    
    img.save(output_path)
    return output_path


def create_deliverable_screenshot(
    screenshot_path: Path,
    x: int,
    y: int,
    position_name: str,
    output_dir: Path = None,
) -> Path:
    """
    Create an annotated screenshot for deliverables.
    
    Args:
        screenshot_path: Path to the desktop screenshot
        x, y: Detected icon coordinates
        position_name: Position description (e.g., "top-left", "center")
        output_dir: Output directory
        
    Returns:
        Path to the annotated screenshot
    """
    if output_dir is None:
        output_dir = screenshot_path.parent
    
    output_path = output_dir / f"notepad_detected_{position_name}.png"
    
    return annotate_screenshot(
        screenshot_path=screenshot_path,
        x=x,
        y=y,
        label=f"Notepad - {position_name}",
        output_path=output_path,
    )
