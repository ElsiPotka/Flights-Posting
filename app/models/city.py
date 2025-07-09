from sqlalchemy import String, Float, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from typing import List

from .base import Base


class City(Base):
    __tablename__ = "cities"

    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    country: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(500), nullable=True)
    latitude: Mapped[float] = mapped_column(Float, nullable=True)
    longitude: Mapped[float] = mapped_column(Float, nullable=True)
    average_rating: Mapped[float] = mapped_column(Float, nullable=True, default=0.0)
    review_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    reviews: Mapped[List["Review"]] = relationship(
        "Review", back_populates="city", cascade="all, delete-orphan"
    )
    photos: Mapped[List["Photo"]] = relationship(
        "Photo",
        back_populates="city",
        cascade="all, delete-orphan",
        order_by="Photo.position",
    )
    departing_flights: Mapped[List["Flight"]] = relationship(
        "Flight", back_populates="origin", foreign_keys="Flight.origin_city_id"
    )
    arriving_flights: Mapped[List["Flight"]] = relationship(
        "Flight",
        back_populates="destination",
        foreign_keys="Flight.destination_city_id",
    )
