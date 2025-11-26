from pydantic import BaseModel
from typing import List
from datetime import datetime


class UserJWTResponse(BaseModel):

    username: str
    roles: List[str]
    iat: datetime
    exp: datetime


