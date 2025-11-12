from pydantic import BaseModel
from typing import Optional, List


class UserCreate(BaseModel):

    username: str
    email: str
    password: str
    roles: Optional[List[str]] = []

