from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel

class ReserveResponse(BaseModel):
    """
    Response model for a flight reservation initiation.
    """
    reservationId: str
    reservationStatus: str
    message: Optional[str] = None

class CheckoutResponse(BaseModel):
    """
    Response model for checkout process.
    """
    reservation_id: str
    status: str  # "reserved" or "confirmed"
    timestamp: datetime
    error_message: Optional[str] = None 