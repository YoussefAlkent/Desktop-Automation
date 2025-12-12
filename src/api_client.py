"""JSONPlaceholder API client."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import List

import requests


@dataclass
class Post:
    """A blog post from JSONPlaceholder."""
    id: int
    user_id: int
    title: str
    body: str


class APIError(Exception):
    """Raised when API requests fail after retries."""
    pass


def fetch_posts(count: int = 10, max_retries: int = 3) -> List[Post]:
    """
    Fetch posts from JSONPlaceholder API with exponential backoff.
    
    Args:
        count: Number of posts to fetch (max 100)
        max_retries: Maximum retry attempts
        
    Returns:
        List of Post objects
        
    Raises:
        APIError: If all retries fail
    """
    url = "https://jsonplaceholder.typicode.com/posts"
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, timeout=10.0)
            response.raise_for_status()
            
            data = response.json()
            posts = []
            
            for item in data[:count]:
                posts.append(Post(
                    id=item["id"],
                    user_id=item["userId"],
                    title=item["title"],
                    body=item["body"]
                ))
            
            return posts
            
        except requests.RequestException as e:
            wait_time = (2 ** attempt)  # Exponential backoff: 1s, 2s, 4s
            print(f"  API request failed (attempt {attempt + 1}/{max_retries}): {e}")
            
            if attempt < max_retries - 1:
                print(f"  Retrying in {wait_time}s...")
                time.sleep(wait_time)
    
    raise APIError(f"Failed to fetch posts after {max_retries} attempts")
