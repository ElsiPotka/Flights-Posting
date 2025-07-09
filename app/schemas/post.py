from datetime import datetime
from typing import List

from pydantic import BaseModel, ConfigDict

from .comment import CommentRead
from .flight import FlightRead
from .paginate import Page
from .user import UserRead


class PostBase(BaseModel):
    title: str
    description: str


class PostCreate(PostBase):
    flight_id: str


class PostUpdate(BaseModel):
    title: str | None = None
    description: str | None = None


class PostRead(PostBase):
    id: str
    like_count: int
    user_id: str
    flight_id: str
    created_at: datetime
    updated_at: datetime | None = None

    author: UserRead
    flight: FlightRead
    comments: List[CommentRead] = []

    model_config = ConfigDict(from_attributes=True)


class PostListResponse(Page[PostRead]):
    pass
