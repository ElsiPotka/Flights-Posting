from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session, selectinload

from app.models.city import City
from app.models.photo import Photo
from app.models.review import Review
from app.schemas.city import CityCreate, CityRead, CityUpdate
from app.schemas.review import ReviewCreate, ReviewRead, ReviewUpdate


def create_city(db: Session, city_in: CityCreate) -> City:
    """
    Create a new city and its associated photos in the database.

    """
    existing_city = db.query(City).filter(City.name == city_in.name).first()
    if existing_city:
        raise HTTPException(
            status_code=400, detail="City with this name already exists"
        )

    city_data = city_in.model_dump(exclude={"photos"})
    db_city = City(**city_data)

    if city_in.photos:
        for photo_schema in city_in.photos:
            photo_db = Photo(**photo_schema.model_dump(), city=db_city)
            db.add(photo_db)

    db.add(db_city)
    db.commit()
    db.refresh(db_city)
    return db_city


def get_city_by_id(db: Session, city_id: str) -> Optional[City]:
    """
    Get a city by its ID, including its photos and reviews.
    """
    return (
        db.query(City)
        .options(selectinload(City.photos), selectinload(City.reviews))
        .filter(City.id == city_id, City.deleted_at.is_(None))
        .first()
    )


def get_cities_paginated(db: Session, page: int = 1, size: int = 20) -> Dict[str, Any]:
    """
    Get a paginated list of all non-deleted cities.

    """
    offset = (page - 1) * size
    query = db.query(City).filter(City.deleted_at.is_(None))
    total = query.count()
    items = (
        query.options(selectinload(City.photos))
        .order_by(City.name)
        .offset(offset)
        .limit(size)
        .all()
    )
    return {"items": items, "total": total, "page": page, "size": size}


def update_city(*, db: Session, db_city: City, city_in: CityUpdate) -> CityRead:
    """
    Update an existing city with new data, enforcing unique names and
    managing the photos relationship correctly, then return a CityRead.
    """
    if city_in.name is not None and city_in.name != db_city.name:
        existing = db.query(City).filter(City.name == city_in.name).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="City with this name already exists"
            )

    update_data = city_in.model_dump(exclude_unset=True, exclude={"photos"})
    for field, value in update_data.items():
        setattr(db_city, field, value)

    if city_in.photos is not None:
        for old in list(db_city.photos):
            db.delete(old)

        for photo_schema in city_in.photos:
            photo_db = Photo(**photo_schema.model_dump(), city=db_city)
            db.add(photo_db)

    # 4. Persist
    db.add(db_city)
    db.commit()
    db.refresh(db_city)

    return CityRead.model_validate(db_city)


def delete_city(db: Session, db_city: City) -> City:
    """
    Soft delete a city by setting its `deleted_at` timestamp.

    """
    if db_city.deleted_at is None:
        db_city.deleted_at = datetime.utcnow()
        db.add(db_city)
        db.commit()
        db.refresh(db_city)
    return db_city


def restore_city(db: Session, city_id: str) -> Optional[City]:
    """
    Restore a soft-deleted city by setting its `deleted_at` to None.

    """
    db_city = db.query(City).filter(City.id == city_id).first()
    if db_city and db_city.deleted_at is not None:
        db_city.deleted_at = None
        db.add(db_city)
        db.commit()
        db.refresh(db_city)
    return db_city


def add_review_to_city(
    *,
    db: Session,
    city: City,
    review_in: ReviewCreate,
    user_id: str,
) -> ReviewRead:
    """
    Add a new review to a city and update the city's aggregate stats.
    Reject if this user has already reviewed the city.
    """
    existing = (
        db.query(Review)
        .filter(Review.city_id == city.id, Review.user_id == user_id)
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=400, detail="You have already reviewed this city"
        )

    db_review = Review(**review_in.model_dump(), city_id=city.id, user_id=user_id)

    current_total = (city.average_rating or 0) * city.review_count
    new_count = city.review_count + 1
    new_total = current_total + review_in.rating

    city.average_rating = new_total / new_count
    city.review_count = new_count

    db.add(db_review)
    db.add(city)
    db.commit()
    db.refresh(db_review)

    return ReviewRead.model_validate(db_review)


def update_review(
    *,
    db: Session,
    review_id: str,
    user_id: str,
    review_in: ReviewUpdate,
) -> ReviewRead:
    """
    Update an existing review (only by its author) and recalculate
    the city's aggregates.
    """
    db_review = db.query(Review).get(review_id)
    if not db_review or db_review.user_id != user_id:
        raise HTTPException(status_code=404, detail="Review not found")

    old_rating = db_review.rating
    new_rating = review_in.rating if review_in.rating is not None else old_rating
    delta = new_rating - old_rating

    if review_in.rating is not None:
        db_review.rating = new_rating
    if review_in.comment is not None:
        db_review.comment = review_in.comment

    city: City = db_review.city
    total_before = (city.average_rating or 0) * city.review_count
    total_after = total_before + delta
    city.average_rating = total_after / city.review_count

    # 5. Persist
    db.add(db_review)
    db.add(city)
    db.commit()
    db.refresh(db_review)

    return ReviewRead.model_validate(db_review)
