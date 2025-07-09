from typing import Annotated

from fastapi import APIRouter, Body, Depends, HTTPException, Path, Query, status
from sqlalchemy.orm import Session

from app.handlers import flight as flight_handler
from app.handlers.auth import get_current_active_user
from app.models.user import User
from app.schemas.flight import (
    FlightCreate,
    FlightListResponse,
    FlightRead,
    FlightUpdate,
)
from app.utils.db import get_db

router = APIRouter(prefix="/flights", tags=["Flights"])


@router.get(
    "/",
    response_model=FlightListResponse,
    summary="Get a paginated list of flights",
)
def list_flights(
    db: Annotated[Session, Depends(get_db)],
    page: Annotated[int, Query(ge=1, description="Page number to retrieve")] = 1,
    size: Annotated[int, Query(ge=1, le=100, description="Flights per page")] = 20,
) -> FlightListResponse:
    """
    Retrieve a paginated list of all flights. This endpoint is public.
    """
    flight_page_data = flight_handler.get_flights_paginated(db=db, page=page, size=size)
    return FlightListResponse(**flight_page_data)


@router.get(
    "/{flight_id}",
    response_model=FlightRead,
    summary="Get a single flight by ID",
)
def read_flight(
    flight_id: Annotated[
        str,
        Path(..., description="The UUID of the flight to retrieve"),
    ],
    db: Annotated[Session, Depends(get_db)],
) -> FlightRead:
    """
    Retrieve the details of a specific flight by its ID. This endpoint is public.
    """
    db_flight = flight_handler.get_flight_by_id(db=db, flight_id=flight_id)
    if db_flight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found",
        )
    return FlightRead.model_validate(db_flight)


@router.post(
    "/",
    response_model=FlightRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new flight",
)
def create_flight(
    flight_in: Annotated[FlightCreate, Body(...)],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> FlightRead:
    """
    Create a new flight. Must be authenticated.
    """
    db_flight = flight_handler.create_flight(db=db, flight_in=flight_in)
    return FlightRead.model_validate(db_flight)


@router.patch(
    "/{flight_id}",
    response_model=FlightRead,
    summary="Update a flight",
)
def update_flight(
    flight_id: Annotated[
        str,
        Path(..., description="The UUID of the flight to update"),
    ],
    flight_in: Annotated[
        FlightUpdate,
        Body(..., description="Fields to update for the flight"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> FlightRead:
    """
    Update the details of an existing flight. Must be authenticated.
    """
    db_flight = flight_handler.get_flight_by_id(db=db, flight_id=flight_id)
    if db_flight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found",
        )

    updated_flight = flight_handler.update_flight(
        db=db, db_flight=db_flight, flight_in=flight_in
    )
    return FlightRead.model_validate(updated_flight)


@router.delete(
    "/{flight_id}",
    status_code=status.HTTP_200_OK,
    summary="Soft-delete a flight",
)
def delete_flight(
    flight_id: Annotated[
        str,
        Path(..., description="The UUID of the flight to soft-delete"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    Soft delete a flight by setting its `deleted_at` timestamp.
    Must be authenticated.
    """
    db_flight = flight_handler.get_flight_by_id(db=db, flight_id=flight_id)
    if db_flight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found",
        )

    flight_handler.soft_delete_flight(db=db, db_flight=db_flight)
    return {"message": "Flight successfully deleted"}


@router.post(
    "/{flight_id}/restore",
    response_model=FlightRead,
    summary="Restore a soft-deleted flight",
)
def restore_flight(
    flight_id: Annotated[
        str,
        Path(..., description="The UUID of the flight to restore"),
    ],
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> FlightRead:
    """
    Restore a soft-deleted flight by clearing its `deleted_at` timestamp.
    Must be authenticated.
    """
    restored_flight = flight_handler.restore_flight(db=db, flight_id=flight_id)
    if restored_flight is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Flight not found or was not deleted",
        )
    return FlightRead.model_validate(restored_flight)
