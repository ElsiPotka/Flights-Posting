from datetime import datetime
from typing import Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.schemas.comment import CommentCreate, CommentUpdate


def create_comment(
    db: Session, *, comment_in: CommentCreate, post_id: str, user_id: str
) -> Comment:
    """
    Create a new comment on a specific post.
    The existence of the parent post should be verified before calling this function.
    """
    db_comment = Comment(**comment_in.model_dump(), post_id=post_id, user_id=user_id)
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def get_comment_by_id(db: Session, comment_id: str) -> Optional[Comment]:
    """
    Get a single non-deleted comment by its ID.
    """
    statement = select(Comment).where(
        and_(Comment.id == comment_id, Comment.deleted_at.is_(None))
    )
    return db.scalars(statement).first()


def update_comment(
    db: Session, *, db_comment: Comment, comment_in: CommentUpdate, user_id: str
) -> Comment:
    """
    Update an existing comment, ensuring the current user is the author.
    """
    if db_comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this comment",
        )

    update_data = comment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_comment, field, value)

    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    return db_comment


def soft_delete_comment(db: Session, *, db_comment: Comment, user_id: str) -> Comment:
    """
    Soft delete a comment, ensuring the current user is the author.
    """
    if db_comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this comment",
        )

    if db_comment.deleted_at is None:
        db_comment.deleted_at = datetime.utcnow()
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
    return db_comment


def restore_comment(db: Session, *, db_comment: Comment, user_id: str) -> Comment:
    """
    Restore a soft-deleted comment, ensuring the current user is the author.
    """
    if db_comment.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to restore this comment",
        )

    if db_comment.deleted_at is not None:
        db_comment.deleted_at = None
        db.add(db_comment)
        db.commit()
        db.refresh(db_comment)
    return db_comment
