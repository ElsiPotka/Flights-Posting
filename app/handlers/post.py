from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.comment import Comment
from app.models.flight import Flight
from app.models.post import Post
from app.schemas.post import PostCreate, PostUpdate


def create_post(db: Session, *, post_in: PostCreate, user_id: str) -> Post:
    """
    Create a new post for a specific flight, authored by a specific user.
    """
    flight = db.scalars(
        select(Flight).where(
            Flight.id == post_in.flight_id, Flight.deleted_at.is_(None)
        )
    ).first()
    if not flight:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Flight with ID {post_in.flight_id} not found.",
        )

    post_data = post_in.model_dump()
    db_post = Post(**post_data, user_id=user_id)
    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def get_post_by_id(db: Session, post_id: str) -> Optional[Post]:
    """
    Get a single non-deleted post by its ID, eagerly loading all relationships.
    """
    statement = (
        select(Post)
        .options(
            selectinload(Post.author),
            selectinload(Post.flight),
            selectinload(Post.comments).selectinload(Comment.author),
        )
        .where(and_(Post.id == post_id, Post.deleted_at.is_(None)))
    )
    return db.scalars(statement).first()


def get_posts_paginated(
    db: Session, page: int, size: int, *, flight_id: str = None
) -> Dict[str, Any]:
    """
    Get a paginated list of non-deleted posts, optionally filtered by flight_id.
    """
    offset = (page - 1) * size
    base_query = select(Post).where(Post.deleted_at.is_(None))

    if flight_id:
        base_query = base_query.where(Post.flight_id == flight_id)

    total_query = select(func.count()).select_from(base_query.subquery())
    total = db.scalar(total_query)

    items_query = (
        base_query.options(
            selectinload(Post.author),
            selectinload(Post.flight),
            selectinload(Post.comments).selectinload(Comment.author),
        )
        .order_by(Post.created_at.desc())
        .offset(offset)
        .limit(size)
    )
    items = db.scalars(items_query).all()

    return {"items": items, "total": total, "page": page, "size": size}


def update_post(
    db: Session, *, db_post: Post, post_in: PostUpdate, user_id: str
) -> Post:
    """
    Update an existing post, ensuring the user is the author.
    """
    if db_post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this post",
        )

    update_data = post_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_post, field, value)

    db.add(db_post)
    db.commit()
    db.refresh(db_post)
    return db_post


def soft_delete_post(db: Session, *, db_post: Post, user_id: str) -> Post:
    """
    Soft delete a post by setting its `deleted_at` timestamp, ensuring the user is the author.
    """
    if db_post.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this post",
        )

    if db_post.deleted_at is None:
        db_post.deleted_at = datetime.utcnow()
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
    return db_post


def restore_post(db: Session, *, post_id: str, user_id: str) -> Optional[Post]:
    """
    Restore a soft-deleted post by its ID, ensuring the user is the author.
    """
    db_post = db.scalars(select(Post).where(Post.id == post_id)).first()

    if db_post and db_post.deleted_at is not None:
        if db_post.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to restore this post",
            )

        db_post.deleted_at = None
        db.add(db_post)
        db.commit()
        db.refresh(db_post)
        return db_post

    return None
