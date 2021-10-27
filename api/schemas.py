"""API schemas."""
from pydantic import BaseModel


class UserRequest(BaseModel):
    """UserRequest schema.

    Attrs:
        user_id: The ID of the user that requested weather data.
    """

    user_id: int
