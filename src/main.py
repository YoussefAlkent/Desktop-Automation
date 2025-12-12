"""
Vision-Based Desktop Automation with Dynamic Icon Grounding

Main entry point for the automation workflow.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import notepad
from . import screenshot
from .annotations import create_deliverable_screenshot
from .api_client import fetch_posts, APIError
from .config import get_config
from .ocr_grounder import ground_icon, GroundingError


def test_grounding() -> int:
    """
    Test the grounding system without running full automation.
    
    Returns:
        0 on success, 1 on failure
    """
    config = get_config()
    
    print("\n" + "=" * 60)
    print("OCR Grounding Test")
    print("=" * 60)
    
    # Show desktop and capture
    print("\n[1] Showing desktop...")
    from . import mouse_keyboard as mk
    mk.show_desktop()
    
    print("[2] Capturing screenshot...")
    screenshot_path = screenshot.capture_desktop(config.screenshots_dir, "grounding_test.png")
    print(f"    Saved: {screenshot_path}")
    
    print("\n[3] Running OCR grounding for 'Notepad'...")
    try:
        result = ground_icon(screenshot_path, "Notepad")
        print(f"\n✓ SUCCESS!")
        print(f"  Icon found at: ({result.x}, {result.y})")
        print(f"  Confidence: {result.confidence:.2f}")
        print(f"  Text matched: '{result.text_found}'")
        
        # Create annotated screenshot
        annotated = create_deliverable_screenshot(
            screenshot_path, result.x, result.y, "test",
            config.screenshots_dir
        )
        print(f"\n  Annotated screenshot: {annotated}")
        return 0
        
    except GroundingError as e:
        print(f"\n✗ FAILED: {e}")
        if e.available_labels:
            print(f"  Available labels: {e.available_labels}")
        return 1


def run_automation(num_posts: int = 10) -> int:
    """
    Run the full automation workflow.
    
    Args:
        num_posts: Number of posts to process
        
    Returns:
        0 on success, 1 on failure
    """
    config = get_config()
    
    print("\n" + "=" * 60)
    print("Vision-Based Desktop Automation")
    print("=" * 60)
    
    print(f"\nConfiguration:")
    print(f"  Output Directory: {config.output_dir}")
    print(f"  Screen Resolution: {config.screen_width}x{config.screen_height}")
    print(f"  Max Retries: {config.max_retries}")
    
    # Fetch posts from API
    print(f"\nFetching {num_posts} posts from JSONPlaceholder API...")
    try:
        posts = fetch_posts(num_posts, max_retries=config.max_retries)
        print(f"  Retrieved {len(posts)} posts")
    except APIError as e:
        print(f"\n✗ API Error: {e}")
        print("Exiting gracefully.")
        return 1
    
    # Process each post
    for i, post in enumerate(posts, 1):
        print(f"\n{'=' * 40}")
        print(f"Processing post {i}/{len(posts)}: ID={post.id}")
        print(f"{'=' * 40}")
        
        try:
            # Launch Notepad
            print("\n[Step 1] Launching Notepad...")
            notepad.launch_notepad_from_desktop()
            
            # Type and save
            print("\n[Step 2] Typing content...")
            filepath = notepad.process_post(
                post.id, post.title, post.body,
                config.output_dir
            )
            print(f"  Saved: {filepath}")
            
            # Close Notepad
            print("\n[Step 3] Closing Notepad...")
            notepad.close_notepad()
            
            print(f"\n✓ Post {post.id} completed!")
            
        except GroundingError as e:
            print(f"\n✗ Grounding Error: {e}")
            if e.available_labels:
                print(f"  Available: {e.available_labels[:10]}")
            print("\nExiting gracefully.")
            return 1
            
        except Exception as e:
            print(f"\n✗ Unexpected Error: {e}")
            print("\nExiting gracefully.")
            return 1
    
    # Success
    print("\n" + "=" * 60)
    print("Automation Complete!")
    print("=" * 60)
    print(f"  Processed: {len(posts)} posts")
    print(f"  Output: {config.output_dir}")
    return 0


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Vision-Based Desktop Automation with Dynamic Icon Grounding"
    )
    parser.add_argument(
        "--posts", "-n",
        type=int,
        default=10,
        help="Number of posts to process (default: 10)"
    )
    parser.add_argument(
        "--test-grounding", "-t",
        action="store_true",
        help="Test grounding only (don't run full automation)"
    )
    
    args = parser.parse_args()
    
    try:
        if args.test_grounding:
            exit_code = test_grounding()
        else:
            exit_code = run_automation(args.posts)
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        sys.exit(1)


if __name__ == "__main__":
    main()
