import logging
from typing import Dict, Any, Optional
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from model.checkout_request import CheckoutRequest
from model.checkout_response import CheckoutResponse

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
async def initiate_checkout(
    flight_id: str,
    payment_method_id: str,
    user_confirmation: bool = False
) -> Dict[str, Any]:
    """
    Initiates a checkout process for a flight reservation.
    
    This tool handles a two-step checkout process:
    1. Reserve the flight (holds the flight for a short period)
    2. Confirm the reservation (finalizes the booking)
    
    The tool will first check if the flight and payment method exist,
    then create a reservation. If user_confirmation is True, it will
    also confirm the reservation.
    
    Args:
        flight_id: ID of the flight to book
        payment_method_id: ID of the payment method to use
        user_confirmation: Whether to confirm the reservation immediately
    
    Returns:
        A dictionary containing:
        - reservation_id: Unique ID for the reservation
        - status: Current status ("reserved" or "confirmed")
        - timestamp: When the action was taken
        - error_message: Any error that occurred (if applicable)
    
    Raises:
        CheckoutError: If the flight or payment method is not found, or if other errors occur
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Processing checkout request: flight_id={flight_id}, payment_method_id={payment_method_id}")
    
    try:
        # Validate flight exists
        if flight_id not in MOCK_FLIGHTS:
            raise CheckoutError(
                f"Flight {flight_id} not found",
                "FLIGHT_NOT_FOUND",
                {
                    "flight_id": flight_id,
                    "available_flights": list(MOCK_FLIGHTS.keys())
                }
            )
            
        # Validate payment method exists
        if payment_method_id not in MOCK_PAYMENT_METHODS:
            raise CheckoutError(
                f"Payment method {payment_method_id} not found",
                "PAYMENT_METHOD_NOT_FOUND",
                {
                    "payment_method_id": payment_method_id,
                    "available_methods": list(MOCK_PAYMENT_METHODS.keys())
                }
            )
        
        # Create reservation
        reservation_id = f"RES_{request_id}"
        status = "confirmed" if user_confirmation else "reserved"
        
        response = {
            "reservation_id": reservation_id,
            "status": status,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[{request_id}] Successfully processed request. Status: {status}")
        return response
        
    except CheckoutError as e:
        logger.error(f"[{request_id}] Checkout error: {str(e)}", exc_info=True)
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
        logger.error(f"[{request_id}] Unexpected error: {str(e)}", exc_info=True)
        raise CheckoutError(
            "An unexpected error occurred while processing the request",
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