from typing import List
from sqlalchemy import String, Text, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Post(Base):
    """
    Represents a user-generated post about a specific flight.
    """

    __tablename__ = "posts"

    title: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    like_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=0, server_default="0"
    )

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    flight_id: Mapped[str] = mapped_column(
        ForeignKey("flights.id"), nullable=False, index=True
    )

    author: Mapped["User"] = relationship(back_populates="posts")
    flight: Mapped["Flight"] = relationship(back_populates="posts")

    comments: Mapped[List["Comment"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )

    likes: Mapped[List["Like"]] = relationship(
        back_populates="post", cascade="all, delete-orphan"
    )
