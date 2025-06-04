from typing import Optional
from pydantic import BaseModel

class ConfirmResponse(BaseModel):
    """
    Response model for a flight reservation confirmation.
    """
    reservationId: str
    reservationStatus: str
    message: Optional[str] = None 