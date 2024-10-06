from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.user_schemas import TokenPayload
from app.utils.auth import decode_jwt


security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    Retrieves the current user based on the provided JWT token.

    Parameters:
        credentials (HTTPAuthorizationCredentials): The HTTP authorization credentials containing the JWT token.

    Returns:
        TokenPayload: A token payload object containing user details such as username and roles.

    Raises:
        HTTPException: If the token is invalid or expired.
    """
    token = credentials.credentials
    payload = decode_jwt(token)
    print(payload)
    return TokenPayload(
        sub=payload['sub'],
        roles=payload.get('cognito:groups', []),
        username=payload['cognito:username']
    )

def role_required(required_role: str):
    """
    A dependency that checks if the current user has the required role.

    Parameters:
        required_role (str): The role that is required to access a specific resource.

    Returns:
        function: A function that verifies the user's role.

    Raises:
        HTTPException: If the user does not have the required role.
    """
    def role_checker(user: TokenPayload = Depends(get_current_user)):
        # print(user)
        if required_role not in user.roles:
            raise HTTPException(status_code=403, detail="You do not have access to this resource")
        return user

    return role_checker
