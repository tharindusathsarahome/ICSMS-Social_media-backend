# app/services/social_media_service.py

from typing import List
from app.api.models.social_media import FacebookPostCreate

async def process_facebook_posts(posts: List[FacebookPostCreate]) -> List[FacebookPostCreate]:
    """
    Process Facebook posts before storing them in MongoDB.
    """
    processed_posts = []

    for post in posts:
        # Remove posts with empty messages
        if post.message.strip():
            processed_posts.append(post)

    return processed_posts
