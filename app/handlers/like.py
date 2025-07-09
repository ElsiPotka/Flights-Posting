from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.models.like import Like
from app.models.post import Post


def toggle_like_post(db: Session, *, db_post: Post, user_id: str) -> Post:
    """
    Toggles a 'like' on a post for a specific user.

    - If the user has already liked the post, the like is removed.
    - If the user has not liked the post, a like is added.

    The post's 'like_count' is updated accordingly in the same transaction.
    """
    statement = select(Like).where(
        and_(Like.post_id == db_post.id, Like.user_id == user_id)
    )
    existing_like = db.scalars(statement).first()

    if existing_like:
        db.delete(existing_like)
        db_post.like_count = max(0, db_post.like_count - 1)
    else:
        new_like = Like(post_id=db_post.id, user_id=user_id)
        db.add(new_like)
        db_post.like_count += 1

    db.add(db_post)
    db.commit()
    db.refresh(db_post)

    return db_post
