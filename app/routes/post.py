from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.handlers import comment as comment_handler
from app.handlers import like as like_handler
from app.handlers import post as post_handler
from app.handlers.auth import get_current_active_user
from app.models.user import User
from app.schemas.comment import CommentCreate, CommentRead, CommentUpdate
from app.schemas.post import (
    PostCreate,
    PostListResponse,
    PostRead,
    PostUpdate,
)
from app.utils.db import get_db

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.post(
    "/",
    response_model=PostRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new post about a flight",
)
def create_post(
    post_in: Annotated[PostCreate, Body(...)],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PostRead:
    """
    Create a new post. The user must be authenticated.
    The post must be linked to a valid, existing flight.
    """
    db_post = post_handler.create_post(db=db, post_in=post_in, user_id=current_user.id)
    return PostRead.model_validate(db_post)


@router.get(
    "/",
    response_model=PostListResponse,
    summary="Get a paginated list of posts with optional search",
)
def list_posts(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Page number")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Items per page")] = 20,
    flight_id: Annotated[
        str | None, Query(description="Optionally filter posts by flight ID")
    ] = None,
    q: Annotated[
        str | None,
        Query(description="Search posts by title (case-insensitive partial match)"),
    ] = None,
    author_id: Annotated[
        str | None, Query(description="Optionally filter posts by author ID")
    ] = None,
) -> PostListResponse:
    """
    Retrieve a paginated list of posts with optional filtering and search.

    Filters:
    - flight_id: Exact match to filter posts by specific flight
    - q: Search query for post titles (case-insensitive partial match)

    This is a public endpoint.
    """
    post_page_data = post_handler.get_posts_paginated(
        db=db, page=page, size=size, flight_id=flight_id, q=q, author_id=author_id
    )
    return PostListResponse(**post_page_data)


@router.get(
    "/{post_id}",
    response_model=PostRead,
    summary="Get a single post by ID",
)
def read_post(
    post_id: Annotated[str, Path(..., description="The UUID of the post")],
    db: Annotated[Session, Depends(get_db)],
) -> PostRead:
    """
    Retrieve a specific post by its ID. Includes author, flight, and comments.
    This is a public endpoint.
    """
    db_post = post_handler.get_post_by_id(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    return PostRead.model_validate(db_post)


@router.patch(
    "/{post_id}",
    response_model=PostRead,
    summary="Update a post",
)
def update_post(
    post_id: Annotated[str, Path(..., description="The UUID of the post to update")],
    post_in: Annotated[PostUpdate, Body(...)],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PostRead:
    """
    Update a post's title or description.
    - Must be authenticated.
    - User must be the author of the post.
    """
    db_post = post_handler.get_post_by_id(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    updated_post = post_handler.update_post(
        db=db, db_post=db_post, post_in=post_in, user_id=current_user.id
    )
    return PostRead.model_validate(updated_post)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a post",
)
def delete_post(
    post_id: Annotated[str, Path(..., description="The UUID of the post to delete")],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Soft-delete a post.
    - Must be authenticated.
    - User must be the author of the post.
    """
    db_post = post_handler.get_post_by_id(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )
    post_handler.soft_delete_post(db=db, db_post=db_post, user_id=current_user.id)
    return {"message": "Post successfully deleted"}


@router.post(
    "/{post_id}/restore",
    response_model=PostRead,
    summary="Restore a soft-deleted post",
)
def restore_post(
    post_id: Annotated[str, Path(..., description="The UUID of the post to restore")],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PostRead:
    """
    Restore a soft-deleted post.
    - Must be authenticated.
    - User must be the author of the post.
    """
    restored_post = post_handler.restore_post(
        db=db, post_id=post_id, user_id=current_user.id
    )
    if restored_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or was not deleted",
        )
    return PostRead.model_validate(restored_post)


@router.post(
    "/{post_id}/comments",
    response_model=CommentRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a comment on a post",
    tags=["Comments"],
)
def create_comment_on_post(
    post_id: Annotated[
        str, Path(..., description="The UUID of the post to comment on")
    ],
    comment_in: Annotated[CommentCreate, Body(...)],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CommentRead:
    """
    Add a new comment to an existing post. Must be authenticated.
    """
    db_post = post_handler.get_post_by_id(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    db_comment = comment_handler.create_comment(
        db=db, comment_in=comment_in, post_id=post_id, user_id=current_user.id
    )
    return CommentRead.model_validate(db_comment)


@router.patch(
    "/{post_id}/comments/{comment_id}",
    response_model=CommentRead,
    summary="Update a comment",
    tags=["Comments"],
)
def update_comment(
    post_id: Annotated[str, Path(..., description="The UUID of the parent post")],
    comment_id: Annotated[
        str, Path(..., description="The UUID of the comment to update")
    ],
    comment_in: Annotated[CommentUpdate, Body(...)],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CommentRead:
    """
    Update a comment. Must be authenticated, and the user must be the author.
    """
    db_comment = comment_handler.get_comment_by_id(db=db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if db_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the specified post",
        )

    updated_comment = comment_handler.update_comment(
        db=db, db_comment=db_comment, comment_in=comment_in, user_id=current_user.id
    )
    return CommentRead.model_validate(updated_comment)


@router.delete(
    "/{post_id}/comments/{comment_id}/delete",
    status_code=status.HTTP_200_OK,
    summary="Delete a comment",
    tags=["Comments"],
)
def delete_comment(
    post_id: Annotated[str, Path(..., description="The UUID of the parent post")],
    comment_id: Annotated[
        str, Path(..., description="The UUID of the comment to delete")
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Soft-delete a comment. Must be authenticated, and the user must be the author.
    """
    db_comment = comment_handler.get_comment_by_id(db=db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if db_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the specified post",
        )

    comment_handler.soft_delete_comment(
        db=db, db_comment=db_comment, user_id=current_user.id
    )
    return {"message": "Comment successfully deleted"}


@router.post(
    "/{post_id}/comments/{comment_id}/restore",
    status_code=status.HTTP_200_OK,
    summary="Restore a soft-deleted comment",
    tags=["Comments"],
)
def restore_comment(
    post_id: Annotated[str, Path(..., description="The UUID of the parent post")],
    comment_id: Annotated[
        str, Path(..., description="The UUID of the comment to restore")
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Restore a soft-deleted comment. Must be authenticated, and the user must be the author.
    """
    db_comment = comment_handler.get_comment_by_id(db=db, comment_id=comment_id)
    if db_comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found"
        )

    if db_comment.post_id != post_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment does not belong to the specified post",
        )

    if db_comment.deleted_at is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Comment is not deleted",
        )

    comment_handler.restore_comment(
        db=db, db_comment=db_comment, user_id=current_user.id
    )
    return {"message": "Comment successfully restored"}


@router.post(
    "/{post_id}/toggle-like",
    response_model=PostRead,
    summary="Toggle a like on a post",
    tags=["Likes"],
)
def toggle_post_like(
    post_id: Annotated[
        str, Path(..., description="The UUID of the post to like/unlike")
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> PostRead:
    """
    Toggles a 'like' on a post for the authenticated user.

    - If the user has not liked the post, it will be liked.
    - If the user has already liked the post, the like will be removed.

    Returns the post with the updated like count.
    """
    db_post = post_handler.get_post_by_id(db=db, post_id=post_id)
    if db_post is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Post not found"
        )

    updated_post = like_handler.toggle_like_post(
        db=db, db_post=db_post, user_id=current_user.id
    )

    return PostRead.model_validate(updated_post)
