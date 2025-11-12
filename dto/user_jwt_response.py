from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserJWTResponse(BaseModel):
    """DTO for user details from JWT token"""
    username: str
    roles: List[str]
    iat: datetime
    exp: datetime


