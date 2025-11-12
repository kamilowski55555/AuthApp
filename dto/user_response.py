from pydantic import BaseModel
from typing import List


class UserResponse(BaseModel):

    id: int
    username: str
    email: str
    roles: List[str]

    class Config:
        from_attributes = True

