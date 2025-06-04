from typing import Optional, Any
from pydantic import BaseModel

class ReserveResponse(BaseModel):
    """
    Response model for a flight reservation initiation.
    """
    reservationId: str
    reservationStatus: str
    message: Optional[str] = None 