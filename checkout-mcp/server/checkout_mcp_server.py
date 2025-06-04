import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path
from datetime import datetime
import httpx # Import httpx

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from model.checkout_request import ReserveRequest
from model.checkout_response import ReserveResponse
from model.confirm_request import ConfirmRequest
from model.confirm_response import ConfirmResponse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Define the base URL for the external service
BASE_SERVICE_URL = "https://safepay-partner-experience-service-mock-qa.dev.aws.jpmchase.net"

# Initialize FastMCP server
mcp = FastMCP("Checkout")

class CheckoutError(Exception):
    """Custom exception for checkout errors."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

@mcp.tool()
async def reserve_flight(
    departureAirportCode: str,
    destinationAirportCode: str,
    departureDate: str,
    arrivalDate: str,
    numberOfPassengers: int,
    paymentMethod: str
) -> Dict[str, Any]:
    """
    Initiates a reservation for a flight by calling the external service.
    
    This tool calls the /travel/reserve endpoint to hold a flight
    and returns the reservation details provided by the service.
    
    Args:
        departureAirportCode: The IATA airport code for the departure location (e.g., 'JFK').
        destinationAirportCode: The IATA airport code for the arrival location (e.g., 'EWR').
        departureDate: The departure date and time in ISO 8601 format (e.g., '2025-06-04T00:00:00.000Z').
        arrivalDate: The arrival date and time in ISO 8601 format (e.g., '2025-06-05T00:00:00.000Z').
        numberOfPassengers: The total number of passengers (integer).
        paymentMethod: Identifier for the payment method to use (e.g., '....1111').
        
    Returns:
        A dictionary containing the reservation details from the external service:
        - reservationId: A unique identifier for the pending reservation.
        - reservationStatus: The status of the reservation (e.g., 'PENDING').
        - message: A human-readable message about the reservation status.
    
    Raises:
        CheckoutError: If the API call fails or returns an error.
        
    Example Conversation:
        User: Can you reserve a flight from JFK to LAX tomorrow?
        Assistant: (Calls reserve_flight with appropriate parameters)
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Calling /travel/reserve endpoint...")
    
    reserve_url = f"{BASE_SERVICE_URL}/travel/reserve"
    payload = {
        "departureAirportCode": departureAirportCode,
        "destinationAirportCode": destinationAirportCode,
        "departureDate": departureDate,
        "arrivalDate": arrivalDate,
        "numberOfPassengers": numberOfPassengers,
        "paymentMethod": paymentMethod
    }
    logger.info(f"[{request_id}] Reserve Request Payload: {payload}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(reserve_url, json=payload)
            response.raise_for_status() # Raise an exception for bad status codes

        response_data = response.json()
        logger.info(f"[{request_id}] Reserve Response: {response_data}")
        return response_data

    except httpx.HTTPStatusError as e:
        logger.error(f"[{request_id}] HTTP error during reservation: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise CheckoutError(
            f"HTTP error during reservation: {e.response.status_code}",
            "HTTP_ERROR",
            {
                "status_code": e.response.status_code,
                "response_text": e.response.text,
                "request_id": request_id
            }
        )
    except httpx.RequestError as e:
        logger.error(f"[{request_id}] Request error during reservation: {str(e)}", exc_info=True)
        raise CheckoutError(
            f"Request error during reservation: {str(e)}",
            "REQUEST_ERROR",
            {
                "error": str(e),
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error during reservation: {str(e)}", exc_info=True)
        raise CheckoutError(
            "An unexpected error occurred during the reservation process",
            "INTERNAL_ERROR",
            {
                "error": str(e),
                "request_id": request_id
            }
        )

@mcp.tool()
async def confirm_reservation(
    reservationId: str
) -> Dict[str, Any]:
    """
    Confirms a pending flight reservation by calling the external service.
    
    This tool calls the /travel/confirm endpoint to finalize a reservation.
    
    Args:
        reservationId: The unique identifier of the reservation to confirm,
                       obtained from the reserve_flight tool.
        
    Returns:
        A dictionary containing the confirmation details from the external service:
        - reservationId: The identifier of the confirmed reservation.
        - reservationStatus: The status of the reservation (e.g., 'CONFIRMED').
        - message: A human-readable message about the confirmation status (e.g., a simple receipt).
    
    Raises:
        CheckoutError: If the API call fails or returns an error.
        
    Example Conversation:
        User: Yes, please confirm the booking.
        Assistant: (Uses the reservationId from the previous reserve_flight call and calls confirm_reservation)
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Calling /travel/confirm endpoint for ID: {reservationId}..."
)

    confirm_url = f"{BASE_SERVICE_URL}/travel/confirm"
    payload = {"reservationId": reservationId}
    logger.info(f"[{request_id}] Confirm Request Payload: {payload}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(confirm_url, json=payload)
            response.raise_for_status() # Raise an exception for bad status codes

        response_data = response.json()
        logger.info(f"[{request_id}] Confirm Response: {response_data}")
        return response_data

    except httpx.HTTPStatusError as e:
        logger.error(f"[{request_id}] HTTP error during confirmation: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise CheckoutError(
            f"HTTP error during confirmation: {e.response.status_code}",
            "HTTP_ERROR",
            {
                "status_code": e.response.status_code,
                "response_text": e.response.text,
                "request_id": request_id
            }
        )
    except httpx.RequestError as e:
        logger.error(f"[{request_id}] Request error during confirmation: {str(e)}", exc_info=True)
        raise CheckoutError(
            f"Request error during confirmation: {str(e)}",
            "REQUEST_ERROR",
            {
                "error": str(e),
                "request_id": request_id
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error during confirmation: {str(e)}", exc_info=True)
        raise CheckoutError(
            "An unexpected error occurred during the confirmation process",
            "INTERNAL_ERROR",
            {
                "error": str(e),
                "request_id": request_id
            }
        )

if __name__ == "__main__":
    logger.info("Starting Checkout MCP server")
    mcp.run() 