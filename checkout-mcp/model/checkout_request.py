from typing import Optional
from pydantic import BaseModel

class CheckoutRequest(BaseModel):
    """
    Request model for checkout process.
    """
    flight_id: str
    payment_method_id: str
    user_confirmation: bool = False 