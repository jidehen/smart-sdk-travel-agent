from pydantic import BaseModel

class ConfirmRequest(BaseModel):
    """
    Request model for confirming a flight reservation.
    """
    reservationId: str 