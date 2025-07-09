from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.handlers.auth import (
    login_for_token,
    login_user,
    register_new_user,
)
from app.schemas.auth_token import AuthResponse, LoginRequest, Token
from app.schemas.user import UserCreate
from app.utils.db import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED
)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Creates a new user and returns the new user object along with access/refresh tokens.
    """

    return register_new_user(db=db, user_data=user_data)


@router.post("/login", response_model=AuthResponse, summary="Login for Users (JSON)")
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    """
    Handles user login via a standard JSON request body.

    This is ideal for your front-end or mobile app clients.
    It returns a rich response including the token and user details.
    """
    return login_user(db=db, login_data=login_data)


@router.post("/token", response_model=Token, summary="Get OAuth2 Token (Form Data)")
def token(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
):
    """
    Handles user login via an OAuth2 compatible form data request.

    """
    return login_for_token(db=db, email=form_data.username, password=form_data.password)
