from typing import Optional
from datetime import datetime
from pydantic import BaseModel

class CheckoutResponse(BaseModel):
    """
    Response model for checkout process.
    """
    reservation_id: str
    status: str  # "reserved" or "confirmed"
    timestamp: datetime
    error_message: Optional[str] = None 