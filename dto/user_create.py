from pydantic import BaseModel
from typing import Optional, List


class UserCreate(BaseModel):
    """DTO for creating a new user"""
    username: str
    email: str
    password: str
    roles: Optional[List[str]] = []

