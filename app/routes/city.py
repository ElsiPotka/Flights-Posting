from typing import Annotated, Any, Dict

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.handlers import city as city_handler
from app.handlers.auth import get_current_active_user
from app.models.user import User
from app.schemas.city import (
    CityCreate,
    CityListResponse,
    CityRead,
    CityUpdate,
)
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate
from app.utils.db import get_db

router = APIRouter(prefix="/cities", tags=["Cities"])


@router.get(
    "/",
    response_model=CityListResponse,
    summary="Get a paginated list of cities",
)
def read_cities(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Page number to retrieve")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Cities per page")] = 20,
) -> CityListResponse:
    """
    Retrieve a paginated list of all non-deleted cities.
    This endpoint is public and does not require authentication.
    """
    city_page_data = city_handler.get_cities_paginated(db=db, page=page, size=size)
    return CityListResponse(**city_page_data)


@router.get(
    "/{city_id}",
    response_model=CityRead,
    summary="Get a single city by ID",
)
def read_city(
    city_id: Annotated[
        str,
        Path(..., description="The UUID of the city to retrieve"),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> CityRead:
    """
    Retrieve the details of a specific city by its ID.
    This endpoint is public.
    """
    db_city = city_handler.get_city_by_id(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )
    # Convert ORM → Pydantic
    return CityRead.model_validate(db_city)


@router.post(
    "/",
    response_model=CityRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new city",
)
def create_city(
    city_in: Annotated[CityCreate, ...],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CityRead:
    """
    Create a new city. Must be authenticated.
    The request body can include a list of photo objects with URLs.
    """
    db_city = city_handler.create_city(db=db, city_in=city_in)
    return CityRead.model_validate(db_city)


@router.patch(
    "/{city_id}",
    response_model=CityRead,
    summary="Update a city",
)
def update_city(
    city_id: Annotated[
        str,
        Path(..., description="The UUID of the city to update"),
    ],
    city_in: Annotated[
        CityUpdate,
        Body(..., description="Fields to update for the city"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CityRead:
    """
    Update the details of an existing city. Must be authenticated.
    """
    db_city = city_handler.get_city_by_id(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )

    updated_city = city_handler.update_city(db=db, db_city=db_city, city_in=city_in)
    return updated_city


@router.delete(
    "/{city_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a city (soft delete)",
)
def delete_city(
    city_id: Annotated[
        str,
        Path(..., description="The UUID of the city to soft-delete"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Dict[str, Any]:
    """
    Soft delete a city by setting its `deleted_at` timestamp.
    Must be authenticated.
    """
    db_city = city_handler.get_city_by_id(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )

    city_handler.delete_city(db=db, db_city=db_city)
    jsonResponse = {
        "message": "City successfully deleted",
        "data": {},
    }

    return jsonResponse


@router.post(
    "/{city_id}/restore",
    response_model=CityRead,
    summary="Restore a soft-deleted city",
)
def restore_city(
    city_id: Annotated[
        str,
        Path(..., description="The UUID of the city to restore"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CityRead:
    """
    Restore a soft-deleted city by clearing its `deleted_at` timestamp.
    Must be authenticated.
    """
    restored = city_handler.restore_city(db=db, city_id=city_id)
    if restored is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found or was not deleted",
        )
    return CityRead.model_validate(restored)


@router.post(
    "/{city_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
    summary="Add a review to a city",
)
def create_city_review(
    city_id: Annotated[
        str,
        Path(..., description="The UUID of the city to review"),
    ],
    review_in: Annotated[
        ReviewCreate,
        Body(..., description="Review payload"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReviewRead:
    """
    Add a new review to a specific city. Must be authenticated.
    The server will automatically use the authenticated user's ID.
    """
    db_city = city_handler.get_city_by_id(db=db, city_id=city_id)
    if db_city is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="City not found",
        )

    return city_handler.add_review_to_city(
        db=db,
        city=db_city,
        review_in=review_in,
        user_id=current_user.id,
    )


@router.patch(
    "/{review_id}",
    response_model=ReviewRead,
    summary="Update your review",
)
def patch_review(
    review_id: Annotated[
        str,
        Path(..., description="The ID of the review to update"),
    ],
    review_in: Annotated[
        ReviewUpdate,
        Body(..., description="Fields to update on your review"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> ReviewRead:
    """
    Allow authenticated users to update their own review.
    """
    return city_handler.update_review(
        db=db,
        review_id=review_id,
        user_id=current_user.id,
        review_in=review_in,
    )
