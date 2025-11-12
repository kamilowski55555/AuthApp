from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional, List
import jwt
import bcrypt
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import User

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
SECRET_KEY = "super_secret_key"  # w praktyce trzymane w zmiennych środowiskowych
ALGORITHM = "HS256"
security = HTTPBearer()


class LoginData(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    roles: Optional[List[str]] = []


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    roles: List[str]

    class Config:
        from_attributes = True


class UserDetailsResponse(BaseModel):
    username: str
    roles: List[str]
    iat: datetime
    exp: datetime


def verify_token(authorization: Optional[str] = Header(None)) -> dict:
    """Verify JWT token from Authorization header"""
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
    """Check if user has ROLE_ADMIN"""
    roles = payload.get("roles", [])
    if "ROLE_ADMIN" not in roles:
        raise HTTPException(status_code=403, detail="Admin access required")
    return payload


@app.post("/login")
def login(data: LoginData, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    username = data.username
    password = data.password.encode('utf-8')

    # Verify user exists in database
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password
    if not bcrypt.checkpw(password, user.hashed_password.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token with roles
    payload = {
        "sub": username,
        "roles": user.roles if user.roles else [],
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(hours=1)
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/users", response_model=UserResponse)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_admin)
):
    """Create a new user (admin only)"""
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == user_data.username).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    # Check if email already exists
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    # Hash password
    hashed_password = bcrypt.hashpw(user_data.password.encode('utf-8'), bcrypt.gensalt())

    # Create new user
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password.decode('utf-8'),
        roles=user_data.roles
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@app.get("/user_details", response_model=UserDetailsResponse)
def get_user_details(payload: dict = Depends(verify_token)):
    """Get user details from JWT token payload"""
    return {
        "username": payload.get("sub"),
        "roles": payload.get("roles", []),
        "iat": datetime.fromtimestamp(payload.get("iat")),
        "exp": datetime.fromtimestamp(payload.get("exp"))
    }

@app.get("/protected")
def protected_route(payload: dict = Depends(verify_token)):
    return {"message": f"Hello {payload['sub']}, you have access to this protected route!"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)