# app/dependencies/facebook_authentication.py

from typing import AsyncGenerator, Dict
from fastapi import HTTPException
import httpx
from facebook import GraphAPI

from app.core.config import FACEBOOK_USER_TOKEN, FACEBOOK_API_VERSION

async def authenticate_with_facebook() -> GraphAPI:
    """
    Authenticates with the Facebook Graph API and returns the GraphAPI object.

    Returns:
        GraphAPI: An instance of the GraphAPI with an access token for making API calls.

    Raises:
        HTTPException: If authentication with Facebook fails.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url=f"https://graph.facebook.com/v{FACEBOOK_API_VERSION}/me?fields=accounts",
                data={"access_token": FACEBOOK_USER_TOKEN},
            )
            response.raise_for_status()
            token = response.json()['accounts']['data'][0]['access_token']
            return GraphAPI(access_token=token)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error authenticating with Facebook: {str(e)}")

async def authenticate_with_instagram() -> GraphAPI:
    """
    Authenticates with Instagram and returns the GraphAPI object.

    Returns:
        GraphAPI: An instance of the GraphAPI with an access token for making API calls.
    """
    return GraphAPI(access_token=FACEBOOK_USER_TOKEN)