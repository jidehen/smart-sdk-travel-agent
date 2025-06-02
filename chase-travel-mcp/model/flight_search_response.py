from pydantic import BaseModel
from typing import List

class Flight(BaseModel):
    """
    Model for a single flight.
    """
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    price: float
    class_type: str

class FlightSearchResponse(BaseModel):
    """
    Response model for flight search results.
    """
    flights: List[Flight] 