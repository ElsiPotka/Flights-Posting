from sqlalchemy import (
    ForeignKey,
    PrimaryKeyConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base


class Like(Base):
    """
    Association object representing a user's "like" on a post.
    The composite primary key ensures a user can only like a post once.
    """

    __tablename__ = "post_likes"
    __table_args__ = (PrimaryKeyConstraint("user_id", "post_id"),)

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    post_id: Mapped[str] = mapped_column(ForeignKey("posts.id"))

    id = None

    user: Mapped["User"] = relationship("User", back_populates="likes")
    post: Mapped["Post"] = relationship("Post", back_populates="likes")
