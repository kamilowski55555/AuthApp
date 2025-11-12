from fastapi import FastAPI, HTTPException, Depends
from datetime import datetime
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from dto import LoginData, UserCreate, UserResponse, UserJWTResponse
from dao import UserDAO
from security import create_access_token, verify_token, require_admin

Base.metadata.create_all(bind=engine)
app = FastAPI()

@app.post("/login")
def login(login_data: LoginData, db: Session = Depends(get_db)):
    """Authenticate user and return JWT token"""
    # Verify user exists in database using DAO
    user = UserDAO.get_by_username(db, login_data.username)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Verify password using DAO
    if not UserDAO.verify_password(user, login_data.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Create JWT token with roles
    token = create_access_token(username=user.username, roles=user.roles if user.roles else [])
    return {"access_token": token, "token_type": "bearer"}

@app.get("/users", response_model=UserResponse)
def get_user_details(payload: dict = Depends(verify_token), db: Session = Depends(get_db)):
    """Get current user details from database"""
    # Get username from JWT payload
    username = payload.get("sub")

    # Fetch user from database
    user = UserDAO.get_by_username(db, username)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        roles=user.roles
    )


@app.post("/users", response_model=UserResponse)
def create_user(
    user_create_dto: UserCreate,
    db: Session = Depends(get_db),
    payload: dict = Depends(require_admin)
):
    """Create a new user (admin only)"""
    # Check if username already exists using DAO
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


@app.get("/user_jwt", response_model=UserJWTResponse)
def get_user_jwt_details(payload: dict = Depends(verify_token)):
    """Get user details from JWT token payload only"""
    return UserJWTResponse(
        username=payload.get("sub"),
        roles=payload.get("roles", []),
        iat=datetime.fromtimestamp(payload.get("iat")),
        exp=datetime.fromtimestamp(payload.get("exp"))
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8080, reload=False)