from sqlalchemy import (
    Text,
    ForeignKey,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Comment(Base):
    """
    Represents a comment made by a user on a specific post.
    """

    __tablename__ = "comments"

    content: Mapped[str] = mapped_column(Text, nullable=False)

    user_id: Mapped[str] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    post_id: Mapped[str] = mapped_column(
        ForeignKey("posts.id"), nullable=False, index=True
    )

    author: Mapped["User"] = relationship(back_populates="comments")
    post: Mapped["Post"] = relationship(back_populates="comments")
