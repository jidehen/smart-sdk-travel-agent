import logging
from typing import List, Dict, Any, Optional
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from model.flight_search_request import FlightSearchRequest
from model.flight_search_response import FlightSearchResponse, Flight

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock flight data
MOCK_FLIGHTS = {
    "JFK-LHR": [
        {
            "airline": "British Airways",
            "flight_number": "BA178",
            "departure_time": "10:00",
            "arrival_time": "22:00",
            "price": 800.00,
            "class": "economy"
        },
        {
            "airline": "American Airlines",
            "flight_number": "AA100",
            "departure_time": "11:00",
            "arrival_time": "23:00",
            "price": 850.00,
            "class": "economy"
        },
        {
            "airline": "United Airlines",
            "flight_number": "UA880",
            "departure_time": "12:00",
            "arrival_time": "00:00",
            "price": 900.00,
            "class": "economy"
        },
        {
            "airline": "Delta",
            "flight_number": "DL400",
            "departure_time": "13:00",
            "arrival_time": "01:00",
            "price": 950.00,
            "class": "economy"
        }
    ]
}

# Initialize FastMCP server
mcp = FastMCP("ChaseTravel")

class TravelSearchError(Exception):
    """Custom exception for travel search errors."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def search_flights_internal(origin: str, destination: str) -> List[Dict[str, Any]]:
    """
    Search for flights between two cities.
    
    Args:
        origin: Origin city code
        destination: Destination city code
        
    Returns:
        List[Dict[str, Any]]: List of available flights
        
    Raises:
        TravelSearchError: If route not found or other errors occur
    """
    logger.info(f"Processing flight search request: {origin} -> {destination}")
    
    if not origin or not destination:
        raise TravelSearchError(
            "Missing origin or destination",
            "MISSING_ROUTE_INFO",
            {"required": "Both origin and destination must be provided"}
        )
    
    route = f"{origin}-{destination}"
    if route not in MOCK_FLIGHTS:
        raise TravelSearchError(
            f"No flights found for route {route}",
            "ROUTE_NOT_FOUND",
            {
                "invalid_route": route,
                "available_routes": list(MOCK_FLIGHTS.keys())
            }
        )
    
    flights = MOCK_FLIGHTS[route]
    logger.info(f"Found {len(flights)} flights for route {route}")
    return flights

@mcp.tool()
async def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    passengers: Optional[Dict[str, int]] = None,
    cabin_class: str = "ECONOMY"
) -> Dict[str, Any]:
    """
    Search for available flights between two airports.
    
    Args:
        origin: IATA airport code for departure (e.g., 'JFK', 'LAX')
        destination: IATA airport code for arrival (e.g., 'LHR', 'CDG')
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Optional return date in YYYY-MM-DD format
        passengers: Optional dict with keys 'adults' (1-9), 'children' (0-9), 'infants' (0-9)
        cabin_class: Desired cabin class (ECONOMY, PREMIUM_ECONOMY, BUSINESS, FIRST)
    
    Returns:
        Dict containing:
        - flights: List of available flights with airline, flight number, times, and price
        - request_id: Unique identifier for the search request
        - timestamp: Request timestamp
    
    Example request:
        {
            "origin": "JFK",
            "destination": "LHR",
            "departure_date": "2024-03-20",
            "passengers": {"adults": 2},
            "cabin_class": "ECONOMY"
        }
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Received flight search request: {origin} -> {destination}")
    
    try:
        flights = search_flights_internal(origin, destination)
        
        response = {
            "flights": flights,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[{request_id}] Successfully processed request. Found {len(flights)} flights")
        return response
        
    except TravelSearchError as e:
        logger.error(f"[{request_id}] Travel search error: {str(e)}", exc_info=True)
        raise TravelSearchError(
            e.message,
            e.error_code,
            {
                **e.details,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
        raise TravelSearchError(
            "An unexpected error occurred while processing the request",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

if __name__ == "__main__":
    logger.info("Starting Chase Travel MCP server")
    mcp.run() 