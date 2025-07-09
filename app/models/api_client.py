from .base import Base
from sqlalchemy.orm import Mapped, mapped_column


class ApiClient(Base):
    __tablename__ = "api_clients"

    client_id: Mapped[str] = mapped_column(primary_key=True, index=True)
    hashed_client_secret: Mapped[str]
    description: Mapped[str]
