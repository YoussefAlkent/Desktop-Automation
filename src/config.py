"""Configuration management."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class Config:
    """Application configuration."""
    
    # Screen settings
    screen_width: int
    screen_height: int
    
    # Output settings
    output_dir: Path
    screenshots_dir: Path
    
    # Retry settings
    max_retries: int
    retry_delay: float
    
    @classmethod
    def load(cls) -> "Config":
        """Load configuration from environment."""
        load_dotenv()
        
        # Output directory on Desktop
        desktop = Path.home() / "Desktop"
        output_dir = desktop / os.getenv("OUTPUT_DIR", "tjm-project")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Screenshots directory
        screenshots_dir = Path.cwd() / "screenshots"
        screenshots_dir.mkdir(parents=True, exist_ok=True)
        
        return cls(
            screen_width=int(os.getenv("SCREEN_WIDTH", "1920")),
            screen_height=int(os.getenv("SCREEN_HEIGHT", "1080")),
            output_dir=output_dir,
            screenshots_dir=screenshots_dir,
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            retry_delay=float(os.getenv("RETRY_DELAY", "1.0")),
        )


# Global config instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config.load()
    return _config
