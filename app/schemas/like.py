from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .user import UserRead


class LikeBase(BaseModel):
    user_id: str
    post_id: str


class LikeRead(LikeBase):
    created_at: datetime
    user: UserRead

    model_config = ConfigDict(from_attributes=True)
