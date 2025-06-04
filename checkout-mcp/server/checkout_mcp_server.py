import logging
import sys
from pathlib import Path
import json
from typing import Dict, Any, Optional
import asyncio
import httpx # Assuming httpx is available for making HTTP requests

# Add the parent directory to Python path (assuming checkout-mcp is at the same level as travel-assistant)
sys.path.append(str(Path(__file__).parent.parent))

# We might need to import FastMCP depending on how the SDK is structured, let's assume it's available
from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("Checkout")

# Define the base URL for the external service based on the Postman screenshot
BASE_SERVICE_URL = "https://safepay-partner-experience-service-mock-qa.dev.aws.jpmchase.net"

class CheckoutError(Exception):
    """Custom exception for checkout errors."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

@mcp.tool()
async def initiate_checkout(
    departureAirportCode: str,
    destinationAirportCode: str,
    departureDate: str,
    arrivalDate: str,
    numberOfPassengers: int,
    paymentMethod: str
) -> Dict[str, Any]:
    """
    Initiates the flight checkout process, reserves the booking, prompts the user for confirmation, and then confirms the booking upon user approval.

    Args:
        departureAirportCode: The IATA airport code for the departure location (e.g., 'JFK').
        destinationAirportCode: The IATA airport code for the arrival location (e.g., 'EWR').
        departureDate: The departure date and time (e.g., '2025-06-04T00:00:00.000Z').
        arrivalDate: The arrival date and time (e.g., '2025-06-05T00:00:00.000Z').
        numberOfPassengers: The total number of passengers (integer).
        paymentMethod: Identifier for the payment method to use (e.g., '....1111').

    Returns:
        A dictionary containing the final booking status and details.
        - 'reservationStatus': The status of the booking (e.g., 'CONFIRMED', 'PENDING', 'FAILED').
        - 'reservationId': The unique identifier for the reservation.
        - 'message': A human-readable message about the booking status.

    Raises:
        CheckoutError: If any step of the checkout process fails.

    Example Conversation:
        User: Can you book this flight for me using my saved card?
        Assistant: (Calls initiate_checkout with flight details and payment method ID)
    """
    logger.info("Initiating checkout process...")
    reservation_id = None

    try:
        # Step 1: Reserve the booking
        reserve_url = f"{BASE_SERVICE_URL}/safepay-partner-experience-service-mock-qa/dev.aws.jpmchase.net/travel/reserve"
        reserve_payload = {
            "departureAirportCode": departureAirportCode,
            "destinationAirportCode": destinationAirportCode,
            "departureDate": departureDate,
            "arrivalDate": arrivalDate,
            "numberOfPassengers": numberOfPassengers,
            "paymentMethod": paymentMethod
        }
        logger.info(f"Sending reserve request to: {reserve_url} with payload: {reserve_payload}")

        async with httpx.AsyncClient() as client:
            reserve_response = await client.post(reserve_url, json=reserve_payload)
            reserve_response.raise_for_status() # Raise an exception for bad status codes

        reserve_data = reserve_response.json()
        reservation_id = reserve_data.get("reservationId")
        reservation_status = reserve_data.get("reservationStatus")
        reserve_message = reserve_data.get("message")

        logger.info(f"Reserve response: Reservation ID: {reservation_id}, Status: {reservation_status}, Message: {reserve_message}")

        if reservation_status != "PENDING":
             raise CheckoutError(
                f"Booking reservation failed with status: {reservation_status}",
                "RESERVATION_FAILED",
                {"reservation_id": reservation_id, "status": reservation_status, "message": reserve_message}
            )

        # Step 2: Prompt user for confirmation (This requires agent interaction - we'll simulate this for now)
        # In a real scenario, the agent would send a TextMessage asking for confirmation
        logger.info(f"Booking reserved with ID {reservation_id}. Prompting user for confirmation...")
        # Simulate waiting for user confirmation. In a real agent, this would involve waiting for the next user message.
        # For this mock MCP, we'll assume confirmation is always given immediately after reservation.
        await asyncio.sleep(1) # Simulate a short delay for user confirmation
        logger.info("Simulating user confirmation received.")

        # Step 3: Confirm the booking
        confirm_url = f"{BASE_SERVICE_URL}/safepay-partner-experience-service-mock-qa/dev.aws.jpmchase.net/travel/confirm"
        confirm_payload = {"reservationId": reservation_id}
        logger.info(f"Sending confirm request to: {confirm_url} with payload: {confirm_payload}")

        async with httpx.AsyncClient() as client:
            confirm_response = await client.post(confirm_url, json=confirm_payload)
            confirm_response.raise_for_status() # Raise an exception for bad status codes

        confirm_data = confirm_response.json()
        confirm_status = confirm_data.get("reservationStatus")
        confirm_message = confirm_data.get("message")

        logger.info(f"Confirm response: Reservation ID: {reservation_id}, Status: {confirm_status}, Message: {confirm_message}")

        if confirm_status != "CONFIRMED":
            raise CheckoutError(
                f"Booking confirmation failed with status: {confirm_status}",
                "CONFIRMATION_FAILED",
                {"reservation_id": reservation_id, "status": confirm_status, "message": confirm_message}
            )

        logger.info(f"Booking successfully confirmed with ID {reservation_id}")
        return {
            "reservationStatus": confirm_status,
            "reservationId": reservation_id,
            "message": confirm_message # This might be null based on screenshot
        }

    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error during checkout: {e.response.status_code} - {e.response.text}", exc_info=True)
        raise CheckoutError(
            f"HTTP error during checkout: {e.response.status_code}",
            "HTTP_ERROR",
            {
                "request_id": reservation_id, # Use reservation_id if available
                "status_code": e.response.status_code,
                "response_text": e.response.text
            }
        )
    except httpx.RequestError as e:
        logger.error(f"Request error during checkout: {str(e)}", exc_info=True)
        raise CheckoutError(
            f"Request error during checkout: {str(e)}",
            "REQUEST_ERROR",
            {"request_id": reservation_id, "error": str(e)}
        )
    except CheckoutError as e:
        # Re-raise our custom errors
        raise e
    except Exception as e:
        logger.error(f"Unexpected error during checkout: {str(e)}", exc_info=True)
        raise CheckoutError(
            "An unexpected error occurred during the checkout process",
            "INTERNAL_ERROR",
            {"request_id": reservation_id, "error": str(e)}
        )

if __name__ == "__main__":
    logger.info("Starting Checkout MCP server")
    mcp.run() 