# app/dependencies/facebook_authentication.py

from typing import AsyncGenerator, Dict
from fastapi import HTTPException
import httpx
from facebook import GraphAPI

from app.core.config import FACEBOOK_USER_TOKEN, FACEBOOK_API_VERSION

async def authenticate_with_facebook() -> GraphAPI:
    """
    Authenticate with Facebook and return the GraphAPI object.
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
    Authenticate with Instagram and return the GraphAPI object.
    """
    return GraphAPI(access_token=FACEBOOK_USER_TOKEN)