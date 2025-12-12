"""OCR-based grounding for desktop icons using EasyOCR."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple

import easyocr
from PIL import Image


@dataclass
class TextLocation:
    """A detected text with its bounding box."""
    text: str
    x: int  # Left
    y: int  # Top  
    width: int
    height: int
    confidence: float
    
    @property
    def center(self) -> Tuple[int, int]:
        """Get center of the text bounding box."""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    @property
    def icon_center(self) -> Tuple[int, int]:
        """
        Get the approximate center of the icon above this text label.
        Desktop icons have text below the icon image.
        """
        cx, cy = self.center
        # Move up from text to icon center (typically ~40-50 pixels)
        return (cx, cy - 45)


@dataclass
class GroundingResult:
    """Result of a grounding operation."""
    x: int
    y: int
    confidence: float
    text_found: str
    
    @property
    def coordinates(self) -> Tuple[int, int]:
        return (self.x, self.y)


class GroundingError(Exception):
    """Raised when grounding fails to find the target."""
    
    def __init__(self, message: str, available_labels: Optional[List[str]] = None):
        super().__init__(message)
        self.available_labels = available_labels or []


class OCRGrounder:
    """
    OCR-based grounding for desktop icons.
    
    Uses EasyOCR to find text labels on screen, then returns
    coordinates above the text where the icon image is located.
    """
    
    def __init__(self, languages: List[str] = None):
        """
        Initialize the OCR grounder.
        
        Args:
            languages: OCR languages (default: ['en'])
        """
        self.languages = languages or ['en']
        self._reader: Optional[easyocr.Reader] = None
    
    @property
    def reader(self) -> easyocr.Reader:
        """Lazy-load the EasyOCR reader."""
        if self._reader is None:
            print("  Loading OCR model (first time may take a moment)...")
            self._reader = easyocr.Reader(self.languages, gpu=False, verbose=False)
        return self._reader
    
    def find_all_text(self, image_path: Path) -> List[TextLocation]:
        """
        Find all text in a screenshot.
        
        Args:
            image_path: Path to the screenshot
            
        Returns:
            List of TextLocation objects
        """
        results = self.reader.readtext(str(image_path))
        
        locations = []
        for bbox, text, conf in results:
            # bbox is [[x1,y1], [x2,y1], [x2,y2], [x1,y2]]
            x1 = int(min(p[0] for p in bbox))
            y1 = int(min(p[1] for p in bbox))
            x2 = int(max(p[0] for p in bbox))
            y2 = int(max(p[1] for p in bbox))
            
            locations.append(TextLocation(
                text=text,
                x=x1,
                y=y1,
                width=x2 - x1,
                height=y2 - y1,
                confidence=conf
            ))
        
        return locations
    
    def ground(self, image_path: Path, target: str) -> GroundingResult:
        """
        Find a desktop icon by its text label.
        
        Args:
            image_path: Path to desktop screenshot
            target: Icon name to find (e.g., "Notepad")
            
        Returns:
            GroundingResult with icon coordinates
            
        Raises:
            GroundingError: If the target is not found
        """
        print(f"  OCR scanning for '{target}'...")
        
        all_text = self.find_all_text(image_path)
        
        if not all_text:
            raise GroundingError("No text found in screenshot", [])
        
        labels = [t.text for t in all_text]
        print(f"  Found {len(all_text)} labels: {labels[:15]}{'...' if len(labels) > 15 else ''}")
        
        # Find matching text
        target_lower = target.lower()
        matched: Optional[TextLocation] = None
        
        # Try exact match first
        for loc in all_text:
            if loc.text.lower() == target_lower:
                matched = loc
                break
        
        # Try partial match
        if not matched:
            for loc in all_text:
                if target_lower in loc.text.lower() or loc.text.lower() in target_lower:
                    matched = loc
                    break
        
        if not matched:
            raise GroundingError(f"'{target}' not found in detected text", labels)
        
        # Get icon center (above the text)
        icon_x, icon_y = matched.icon_center
        
        print(f"  Found '{matched.text}' → icon at ({icon_x}, {icon_y})")
        
        return GroundingResult(
            x=icon_x,
            y=icon_y,
            confidence=matched.confidence,
            text_found=matched.text
        )


# Global grounder instance for reuse
_grounder: Optional[OCRGrounder] = None


def get_grounder() -> OCRGrounder:
    """Get the global OCR grounder instance."""
    global _grounder
    if _grounder is None:
        _grounder = OCRGrounder()
    return _grounder


def ground_icon(image_path: Path, target: str) -> GroundingResult:
    """
    Convenience function to ground an icon.
    
    Args:
        image_path: Path to screenshot
        target: Icon name to find
        
    Returns:
        GroundingResult with coordinates
    """
    return get_grounder().ground(image_path, target)
