import requests
from fastapi import HTTPException
from jose import JWTError, jwt
from app.core.config import COGNITO_REGION, COGNITO_POOL_ID, COGNITO_APP_CLIENT_ID, S3_BUCKET_NAME

cognito_keys_url = f'https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{COGNITO_POOL_ID}/.well-known/jwks.json'

def get_cognito_public_keys():
    response = requests.get(cognito_keys_url)
    response.raise_for_status()
    return response.json()['keys']


cognito_public_keys = get_cognito_public_keys()


def decode_jwt(token: str):
    global cognito_public_keys
    try:
        header = jwt.get_unverified_header(token)
        key = next(k for k in cognito_public_keys if k['kid'] == header['kid'])
        return jwt.decode(token, key, algorithms=['RS256'], audience=COGNITO_APP_CLIENT_ID)
    except JWTError:
        # If verification fails, try to fetch the keys again
        header = jwt.get_unverified_header(token)
        cognito_public_keys = get_cognito_public_keys()
        try:
            key = next(k for k in cognito_public_keys if k['kid'] == header['kid'])
            return jwt.decode(token, key, algorithms=['RS256'], audience=COGNITO_APP_CLIENT_ID)
        except JWTError:
            raise HTTPException(status_code=403, detail="Could not validate credentials")
