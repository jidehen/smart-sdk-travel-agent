from typing import Optional
from pydantic import BaseModel

class FlightSearchRequest(BaseModel):
    """
    Request model for flight search.
    """
    origin: str
    destination: str
    departure_date: str
    return_date: Optional[str] = None
    passengers: int = 1
    class_type: str = "economy" 