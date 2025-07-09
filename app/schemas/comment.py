from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .user import UserRead


class CommentBase(BaseModel):
    content: str


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    content: str | None = None


class CommentRead(CommentBase):
    id: str
    user_id: str
    post_id: str
    created_at: datetime
    updated_at: datetime | None = None
    author: UserRead

    model_config = ConfigDict(from_attributes=True)
