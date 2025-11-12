from pydantic import BaseModel


class LoginData(BaseModel):
    """DTO for login request"""
    username: str
    password: str