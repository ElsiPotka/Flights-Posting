from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class PhotoBase(BaseModel):
    url: str = Field(..., description="URL to the photo stored in media")
    caption: Optional[str] = Field(None, description="Optional caption for the photo")
    position: int = Field(0, ge=0, description="Ordering position of the photo")


class PhotoCreate(PhotoBase):
    city_id: str = Field(
        ..., description="UUID of the existing city to attach this photo to"
    )


class PhotoRead(PhotoBase):
    id: str
    city_id: str
    created_at: datetime | None = None
    updated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
