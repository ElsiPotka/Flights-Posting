from sqlalchemy import String, DateTime, Text, Enum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
import enum
from .base import Base
from typing import List


class FlightStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    BOARDING = "boarding"
    DEPARTED = "departed"
    ARRIVED = "arrived"
    DELAYED = "delayed"
    CANCELED = "canceled"


class Flight(Base):
    __tablename__ = "flights"

    flight_number: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True, index=True
    )
    airline: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    origin_city_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cities.id"), nullable=False, index=True
    )
    origin: Mapped["City"] = relationship(
        "City", foreign_keys=[origin_city_id], back_populates="departing_flights"
    )

    destination_city_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("cities.id"), nullable=False, index=True
    )
    destination: Mapped["City"] = relationship(
        "City", foreign_keys=[destination_city_id], back_populates="arriving_flights"
    )

    status: Mapped[FlightStatus] = mapped_column(
        Enum(FlightStatus, name="flight_status"),
        nullable=False,
        default=FlightStatus.SCHEDULED,
    )

    departure: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    arrival: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    posts: Mapped[List["Post"]] = relationship(
        back_populates="flight", cascade="all, delete-orphan"
    )
