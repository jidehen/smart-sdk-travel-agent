import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path
import json
from datetime import datetime

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

# Mock data for testing
MOCK_FLIGHTS = {
    "FL123": {"origin": "JFK", "destination": "LAX", "price": 299.99},
    "FL456": {"origin": "SFO", "destination": "ORD", "price": 199.99},
}

MOCK_PAYMENT_METHODS = {
    "PM789": {"type": "credit_card", "last4": "1234"},
    "PM012": {"type": "debit_card", "last4": "5678"},
}

# In-memory storage for reservations (for mock purposes)
RESERVATIONS: Dict[str, Dict[str, Any]] = {}

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
    Initiates a reservation for a flight.
    
    This tool simulates the first step of the checkout process,
    holding a flight for a short period and returning a pending reservation ID.
    
    Args:
        departureAirportCode: The IATA airport code for the departure location (e.g., 'JFK').
        destinationAirportCode: The IATA airport code for the arrival location (e.g., 'EWR').
        departureDate: The departure date and time (e.g., '2025-06-04T00:00:00.000Z').
        arrivalDate: The arrival date and time (e.g., '2025-06-05T00:00:00.000Z').
        numberOfPassengers: The total number of passengers (integer).
        paymentMethod: Identifier for the payment method to use (e.g., '....1111').
        
    Returns:
        A dictionary containing the reservation details:
        - reservationId: A unique identifier for the pending reservation.
        - reservationStatus: The status of the reservation (always 'PENDING' for this step).
        - message: A human-readable message about the reservation status.
    
    Raises:
        CheckoutError: If the flight or payment method is not found, or if other errors occur.
        
    Example Conversation:
        User: Can you reserve a flight from JFK to LAX tomorrow?
        Assistant: (Calls reserve_flight with appropriate parameters)
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Processing flight reservation request: {departureAirportCode} to {destinationAirportCode}")
    
    try:
        # Simulate checking flight and payment method existence (simplified)
        # In a real scenario, you'd validate against actual mock data or external service
        if not (departureAirportCode and destinationAirportCode and departureDate and paymentMethod):
             raise CheckoutError(
                "Missing required reservation details",
                "MISSING_DETAILS",
                {}
            )
        
        # Simulate creating a pending reservation
        # reservation_id = f"RES_{request_id}" # Comment out dynamic ID generation
        reservation_id = "55f0b400-e29b-41d4-a716-446655440000" # Use the hardcoded ID for mock testing
        RESERVATIONS[reservation_id] = {
            "departureAirportCode": departureAirportCode,
            "destinationAirportCode": destinationAirportCode,
            "departureDate": departureDate,
            "arrivalDate": arrivalDate,
            "numberOfPassengers": numberOfPassengers,
            "paymentMethod": paymentMethod,
            "reservationStatus": "PENDING",
            "created_at": datetime.now()
        }
        
        response = {
            "reservationId": reservation_id,
            "reservationStatus": "PENDING",
            "message": f"Reservation {reservation_id} created successfully. Awaiting confirmation."
        }
        
        logger.info(f"[{request_id}] Successfully created pending reservation {reservation_id}")
        return response
        
    except CheckoutError as e:
        logger.error(f"[{request_id}] Reservation error: {str(e)}", exc_info=True)
        raise CheckoutError(
            e.message,
            e.error_code,
            {
                **e.details,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error during reservation: {str(e)}", exc_info=True)
        raise CheckoutError(
            "An unexpected error occurred during the reservation process",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

@mcp.tool()
async def confirm_reservation(
    reservationId: str
) -> Dict[str, Any]:
    """
    Confirms a pending flight reservation.
    
    This tool simulates the second step of the checkout process,
    finalizing a previously initiated reservation using its ID.
    
    Args:
        reservationId: The unique identifier of the reservation to confirm,
                       obtained from the reserve_flight tool.
        
    Returns:
        A dictionary containing the confirmation details:
        - reservationId: The identifier of the confirmed reservation.
        - reservationStatus: The status of the reservation (always 'CONFIRMED' for this step).
        - message: A human-readable message about the confirmation status (e.g., a simple receipt).
    
    Raises:
        CheckoutError: If the reservation ID is not found, is not pending, or other errors occur.
        
    Example Conversation:
        User: Yes, please confirm the booking.
        Assistant: (Uses the reservationId from the previous reserve_flight call and calls confirm_reservation)
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Processing reservation confirmation request for ID: {reservationId}")
    
    try:
        # Check if the reservation exists and is pending
        if reservationId not in RESERVATIONS:
            raise CheckoutError(
                f"Reservation ID {reservationId} not found",
                "RESERVATION_NOT_FOUND",
                {"reservationId": reservationId}
            )
            
        reservation = RESERVATIONS[reservationId]
        if reservation["reservationStatus"] != "PENDING":
             raise CheckoutError(
                f"Reservation ID {reservationId} is not pending (current status: {reservation['reservationStatus']})",
                "RESERVATION_NOT_PENDING",
                {"reservationId": reservationId, "current_status": reservation["reservationStatus"]}
            )
            
        # Simulate confirming the reservation
        reservation["reservationStatus"] = "CONFIRMED"
        reservation["confirmed_at"] = datetime.now()
        
        response = {
            "reservationId": reservationId,
            "reservationStatus": "CONFIRMED",
            "message": f"Reservation {reservationId} confirmed successfully."
        }
        
        logger.info(f"[{request_id}] Successfully confirmed reservation {reservationId}")
        return response
        
    except CheckoutError as e:
        logger.error(f"[{request_id}] Confirmation error: {str(e)}", exc_info=True)
        raise CheckoutError(
            e.message,
            e.error_code,
            {
                **e.details,
                "request_id": request_id,
                "timestamp": datetime.now().isoformat()
            }
        )
    except Exception as e:
        logger.error(f"[{request_id}] Unexpected error during confirmation: {str(e)}", exc_info=True)
        raise CheckoutError(
            "An unexpected error occurred during the confirmation process",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

if __name__ == "__main__":
    logger.info("Starting Checkout MCP server")
    mcp.run() 