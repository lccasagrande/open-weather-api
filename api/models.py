"""Database schemas."""
from sqlalchemy import JSON, Column, DateTime, Integer

from api.database import Base


class UserRequest(Base):
    """UserRequest table schema.

    Attrs:
        user_id: The ID of the user that requested weather data.
        request_time: The request datetime.
        data: a JSON with city weather.
    """

    __tablename__ = "user_request"

    user_id = Column(Integer, primary_key=True, index=True)
    request_time = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)
