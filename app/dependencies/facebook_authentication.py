# app/dependencies/facebook_authentication.py

from typing import AsyncGenerator, Dict
from fastapi import Depends, HTTPException
from httpx import AsyncClient, Response
from facebook import GraphAPI

from app.core.config import FACEBOOK_USER_TOKEN, FACEBOOK_API_VERSION

async def get_facebook_client() -> AsyncClient:
    return AsyncClient()


async def authenticate_with_facebook(
    client: AsyncClient = Depends(get_facebook_client)
) -> str:
    """
    Authenticate with Facebook and return the access token.
    """
    try:
        response = await client.post(
            url="https://graph.facebook.com/v" + FACEBOOK_API_VERSION + "/me?fields=accounts",
            data={
                "access_token": FACEBOOK_USER_TOKEN
            },
        )
        response.raise_for_status()
        token = response.json()['accounts']['data'][0]['access_token']
        return GraphAPI(token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error authenticating with Facebook: {str(e)}")
    