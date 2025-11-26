from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime
from typing import List
from sqlalchemy.orm import Session
from db.database import get_db
from api.dto import LoginData, UserCreate, UserResponse, UserJWTResponse
from dao import UserDAO
from security import create_access_token, verify_token, require_admin

router = APIRouter(tags=["Authentication"])


@router.post("/login")
def login(login_data: LoginData, db: Session = Depends(get_db)):
    user = UserDAO.get_by_username(db, login_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if not UserDAO.verify_password(user, login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(username=user.username, roles=user.roles if user.roles else [])
    return {"access_token": token, "token_type": "bearer"}


@router.get("/users", response_model=List[UserResponse])
def get_users(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    users = UserDAO.get_all(db)

    return [
        UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            roles=user.roles
        )
        for user in users
    ]


@router.post("/users", response_model=UserResponse)
def create_user(
    user_create_dto: UserCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_admin)
):
    existing_user = UserDAO.get_by_username(db, user_create_dto.username)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")

    existing_email = UserDAO.get_by_email(db, user_create_dto.email)
    if existing_email:
        raise HTTPException(status_code=400, detail="Email already exists")

    new_user = UserDAO.create_user(
        db=db,
        username=user_create_dto.username,
        email=user_create_dto.email,
        password=user_create_dto.password,
        roles=user_create_dto.roles
    )

    return UserResponse(
        id=new_user.id,
        username=new_user.username,
        email=new_user.email,
        roles=new_user.roles
    )


@router.get("/user_jwt", response_model=UserJWTResponse)
def get_user_jwt_details(payload: dict = Depends(verify_token)):
    return UserJWTResponse(
        username=payload.get("sub"),
        roles=payload.get("roles", []),
        iat=datetime.fromtimestamp(payload.get("iat")),
        exp=datetime.fromtimestamp(payload.get("exp"))
    )

