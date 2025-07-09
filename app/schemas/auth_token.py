from pydantic import BaseModel, EmailStr

from app.schemas.user import UserOut


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str


class TokenData(BaseModel):
    email: EmailStr | None = None


class AuthResponse(BaseModel):
    token: Token
    user: UserOut


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
