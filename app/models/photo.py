from .base import Base
from sqlalchemy import String, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship


class Photo(Base):
    __tablename__ = "photos"

    city_id: Mapped[str] = mapped_column(
        ForeignKey("cities.id"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    caption: Mapped[str] = mapped_column(String(200), nullable=True)
    position: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    city: Mapped["City"] = relationship("City", back_populates="photos")
