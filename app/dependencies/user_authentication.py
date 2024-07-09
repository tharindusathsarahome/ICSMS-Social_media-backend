from fastapi import Depends, HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.schemas.user_schemas import TokenPayload
from app.utils.auth import decode_jwt


security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_jwt(token)
    print(payload)
    return TokenPayload(
        sub=payload['sub'],
        roles=payload.get('cognito:groups', []),
        username=payload['cognito:username']
    )

def role_required(required_role: str):
    def role_checker(user: TokenPayload = Depends(get_current_user)):
        # print(user)
        if required_role not in user.roles:
            raise HTTPException(status_code=403, detail="You do not have access to this resource")
        return user

    return role_checker
