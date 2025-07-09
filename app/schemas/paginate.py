import math
from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field, computed_field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """
    A generic pagination schema that can be used to return a paginated
    list of any resource.
    """

    items: List[T]

    total: int = Field(..., description="Total number of items in the database.")
    page: int = Field(..., ge=1, description="Current page number.")
    size: int = Field(..., ge=1, description="Number of items per page.")

    @computed_field
    @property
    def pages(self) -> int:
        """The total number of pages."""
        if self.total <= 0 or self.size <= 0:
            return 0
        return math.ceil(self.total / self.size)

    @computed_field
    @property
    def has_next(self) -> bool:
        """True if there is a next page."""
        return self.page < self.pages

    @computed_field
    @property
    def has_previous(self) -> bool:
        """True if there is a previous page."""
        return self.page > 1
