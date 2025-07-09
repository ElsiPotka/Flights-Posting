from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session, selectinload

from app.models.city import City
from app.models.flight import Flight
from app.schemas.flight import FlightCreate, FlightUpdate


def check_cities_exist(db: Session, origin_city_id: str, destination_city_id: str):
    """Checks if both origin and destination cities exist in the database."""
    city_ids = {origin_city_id, destination_city_id}
    found_cities = db.scalars(select(City.id).where(City.id.in_(city_ids))).all()
    if len(found_cities) != len(city_ids):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Origin or destination city not found.",
        )


def create_flight(db: Session, flight_in: FlightCreate) -> Flight:
    """
    Create a new flight in the database.
    """
    existing_flight = db.scalars(
        select(Flight).where(Flight.flight_number == flight_in.flight_number)
    ).first()
    if existing_flight:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Flight with this flight number already exists.",
        )

    check_cities_exist(db, flight_in.origin_city_id, flight_in.destination_city_id)

    db_flight = Flight(**flight_in.model_dump())
    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight


def get_flight_by_id(db: Session, flight_id: str) -> Optional[Flight]:
    """
    Get a non-deleted flight by its ID, eagerly loading relationships.
    """
    statement = (
        select(Flight)
        .options(selectinload(Flight.origin), selectinload(Flight.destination))
        .where(and_(Flight.id == flight_id, Flight.deleted_at.is_(None)))
    )
    return db.scalars(statement).first()


def get_flights_paginated(db: Session, page: int, size: int) -> Dict[str, Any]:
    """
    Get a paginated list of non-deleted flights.
    """
    offset = (page - 1) * size
    base_query = select(Flight).where(Flight.deleted_at.is_(None))

    total_query = select(func.count()).select_from(base_query.subquery())
    total = db.scalar(total_query)

    items_query = (
        base_query.options(
            selectinload(Flight.origin), selectinload(Flight.destination)
        )
        .order_by(Flight.departure)
        .offset(offset)
        .limit(size)
    )
    items = db.scalars(items_query).all()

    return {"items": items, "total": total, "page": page, "size": size}


def update_flight(db: Session, db_flight: Flight, flight_in: FlightUpdate) -> Flight:
    """
    Update an existing flight with new data.
    """
    update_data = flight_in.model_dump(exclude_unset=True)

    if (
        "flight_number" in update_data
        and update_data["flight_number"] != db_flight.flight_number
    ):
        existing = db.scalars(
            select(Flight).where(Flight.flight_number == update_data["flight_number"])
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Flight with this flight number already exists.",
            )

    if "origin_city_id" in update_data or "destination_city_id" in update_data:
        check_cities_exist(
            db,
            update_data.get("origin_city_id", db_flight.origin_city_id),
            update_data.get("destination_city_id", db_flight.destination_city_id),
        )

    for field, value in update_data.items():
        setattr(db_flight, field, value)

    db.add(db_flight)
    db.commit()
    db.refresh(db_flight)
    return db_flight


def soft_delete_flight(db: Session, db_flight: Flight) -> Flight:
    """
    Soft delete a flight by setting its `deleted_at` timestamp.
    """
    if db_flight.deleted_at is None:
        db_flight.deleted_at = datetime.utcnow()
        db.add(db_flight)
        db.commit()
        db.refresh(db_flight)
    return db_flight


def restore_flight(db: Session, flight_id: str) -> Optional[Flight]:
    """
    Restore a soft-deleted flight by finding it and setting `deleted_at` to None.
    """
    statement = select(Flight).where(Flight.id == flight_id)
    db_flight = db.scalars(statement).first()

    if db_flight and db_flight.deleted_at is not None:
        db_flight.deleted_at = None
        db.add(db_flight)
        db.commit()
        db.refresh(db_flight)
        return db_flight

    return None
