# app/dependencies/facebook.py

from typing import AsyncGenerator, Dict
from fastapi import Depends, HTTPException
from httpx import AsyncClient, Response
from app.core.config import PAGE_ID, ACCESS_TOKEN
from app.core.config import FACEBOOK_API_VERSION

async def get_facebook_client() -> AsyncClient:
    return AsyncClient()


async def fetch_facebook_posts(
    limit: int,
    page_id: str = PAGE_ID,
    client: AsyncClient = Depends(get_facebook_client),
    access_token: str = ACCESS_TOKEN,
) -> AsyncGenerator[Dict, None]:
    """
    Fetch Facebook posts from the Graph API for a given page.
    """
    try:
        url = f"https://graph.facebook.com/v{FACEBOOK_API_VERSION}/{page_id}/posts"
        params = {
            "limit": limit,
            "access_token": access_token,
        }

        async with client.stream("GET", url, params=params) as response_stream:
            async for chunk in response_stream.aiter_text():
                yield chunk

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching Facebook posts: {str(e)}")
