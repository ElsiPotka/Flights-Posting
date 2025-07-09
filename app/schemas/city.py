from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from .paginate import Page
from .photo import PhotoBase, PhotoRead
from .review import ReviewRead


class CityBase(BaseModel):
    name: str = Field(..., max_length=100, description="Name of the city/place")
    country: str = Field(..., max_length=100, description="Country of the city")
    description: Optional[str] = Field(
        None, max_length=500, description="Optional description"
    )
    latitude: Optional[float] = Field(None, description="Latitude coordinate")
    longitude: Optional[float] = Field(None, description="Longitude coordinate")


class CityCreate(CityBase):
    """Schema for creating a new city/place"""

    photos: Optional[List[PhotoBase]] = Field(
        default_factory=list,
        description="List of photos to be associated with the city",
    )


class CityUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    country: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    photos: Optional[List[PhotoBase]] = Field(
        default_factory=list,
        description="List of photos to be associated with the city",
    )


class CityRead(CityBase):
    id: str
    average_rating: Optional[float]
    review_count: int
    created_at: datetime | None = None
    updated_at: datetime | None = None
    deleted_at: Optional[datetime] = None
    reviews: List[ReviewRead] = []
    photos: List[PhotoRead] = []

    model_config = ConfigDict(from_attributes=True)


class CityListResponse(Page[CityRead]):
    """
    The response model for a paginated list of cities.

    This is a concrete implementation of the generic Page schema,
    specialized to contain a list of CityRead items.
    """

    pass
