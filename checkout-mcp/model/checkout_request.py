from typing import Optional
from pydantic import BaseModel

class ReserveRequest(BaseModel):
    """
    Request model for initiating a flight reservation.
    """
    departureAirportCode: str
    destinationAirportCode: str
    departureDate: str
    arrivalDate: str
    numberOfPassengers: int
    paymentMethod: str 