import enum
from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .city import CityRead
from .paginate import Page


class FlightStatus(str, enum.Enum):
    SCHEDULED = "scheduled"
    BOARDING = "boarding"
    DEPARTED = "departed"
    ARRIVED = "arrived"
    DELAYED = "delayed"
    CANCELED = "canceled"


class FlightBase(BaseModel):
    flight_number: str
    airline: str
    description: str | None = None
    origin_city_id: str
    destination_city_id: str
    status: FlightStatus = FlightStatus.SCHEDULED
    departure: datetime
    arrival: datetime


class FlightCreate(FlightBase):
    pass


class FlightUpdate(BaseModel):
    flight_number: str | None = None
    airline: str | None = None
    description: str | None = None
    origin_city_id: str | None = None
    destination_city_id: str | None = None
    status: FlightStatus | None = None
    departure: datetime | None = None
    arrival: datetime | None = None


class FlightRead(FlightBase):
    id: str

    origin: CityRead
    destination: CityRead

    model_config = ConfigDict(from_attributes=True)


class FlightListResponse(Page[FlightRead]):
    """
    The response model for a paginated list of flights.
    """

    pass
