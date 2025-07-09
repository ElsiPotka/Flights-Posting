from .base import Base
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Review(Base):
    __tablename__ = "reviews"

    city_id: Mapped[str] = mapped_column(
        ForeignKey("cities.id"), nullable=False, index=True
    )
    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str] = mapped_column(String(1000), nullable=True)

    city: Mapped["City"] = relationship("City", back_populates="reviews")
    user: Mapped["User"] = relationship("User", back_populates="reviews")
