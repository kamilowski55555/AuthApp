from fastapi import HTTPException, Depends, Header
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt

SECRET_KEY = "super_secret_key"
ALGORITHM = "HS256"


def create_access_token(username: str, roles: list) -> str:

    payload = {
        "sub": username,
        "roles": roles if roles else [],
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(authorization: Optional[str] = Header(None)) -> dict:

    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing")

    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header format")

    token = authorization.split("Bearer ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_admin(payload: dict = Depends(verify_token)) -> dict:

    roles = payload.get("roles", [])
    if "ROLE_ADMIN" not in roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload

