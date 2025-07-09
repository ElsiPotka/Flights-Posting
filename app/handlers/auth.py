from fastapi import Depends, HTTPException, status
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.config.auth import (
    create_access_token,
    create_refresh_token,
    oauth2_scheme,
    verify_token,
)
from app.models.user import User as UserModel
from app.schemas.auth_token import AuthResponse, LoginRequest, Token, TokenData
from app.schemas.user import UserCreate
from app.utils.db import get_db

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_user_by_email(db: Session, email: str) -> UserModel | None:
    return db.query(UserModel).filter(UserModel.email == email).first()


def authenticate_user(db: Session, email: str, password: str) -> UserModel:
    """
    Finds a user by email and verifies their password.
    Returns the user object if successful, otherwise raises HTTPException.
    This is the core, shared logic for all login flows.
    """
    user = get_user_by_email(db, email=email)
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def create_user(db: Session, user: UserCreate) -> UserModel:
    """
    Core function to create a user entry in the database.
    """
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def register_new_user(db: Session, user_data: UserCreate) -> AuthResponse:
    """
    Handles the complete user registration business logic.
    """
    existing_user = get_user_by_email(db, email=user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists.",
        )

    new_user = create_user(db=db, user=user_data)

    token_payload = {"sub": new_user.email}
    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)

    token = Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )

    return AuthResponse(token=token, user=new_user)


def login_user(db: Session, login_data: LoginRequest) -> AuthResponse:
    """
    Handles the user login for the JSON endpoint (/login).
    It now uses the shared authenticate_user function.
    """
    user = authenticate_user(db, email=login_data.email, password=login_data.password)

    token_payload = {"sub": user.email}
    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)
    token_model = Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )
    return AuthResponse(token=token_model, user=user)


def login_for_token(db: Session, email: str, password: str) -> Token:
    """
    Handles user login for the OAuth2 form endpoint (/token).
    It uses the shared authenticate_user function and returns the flat Token model.
    """
    user = authenticate_user(db, email=email, password=password)

    token_payload = {"sub": user.email}
    access_token = create_access_token(data=token_payload)
    refresh_token = create_refresh_token(data=token_payload)

    return Token(
        access_token=access_token, token_type="bearer", refresh_token=refresh_token
    )


def get_current_active_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> UserModel:
    """
    Dependency to get the current user from a token.
    1. Verifies the token using the existing logic.
    2. Fetches the user from the database.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data: TokenData = verify_token(
        token=token, credentials_exception=credentials_exception
    )

    user = get_user_by_email(db, email=token_data.email)

    if user is None:

        raise credentials_exception

    return user
