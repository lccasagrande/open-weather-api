from sqlalchemy import JSON, Column, DateTime, Integer

from .database import Base


class UserRequest(Base):
    __tablename__ = "user_request"

    user_id = Column(Integer, primary_key=True, index=True)
    request_time = Column(DateTime, nullable=False)
    data = Column(JSON, nullable=False)
