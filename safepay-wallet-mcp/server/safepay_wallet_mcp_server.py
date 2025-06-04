import logging
from typing import List, Dict, Any
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock user data with their payment methods
MOCK_USERS = {
    "user1": {
        "name": "John Doe",
        "payment_methods": [
            {
                "card_id": "card_001",
                "type": "credit",
                "brand": "Chase Freedom",
                "last4": "1234",
                "nickname": "Freedom Card"
            },
            {
                "card_id": "card_002",
                "type": "credit",
                "brand": "Chase Sapphire Preferred",
                "last4": "5678",
                "nickname": "Sapphire Card"
            }
        ]
    },
    "user2": {
        "name": "Jane Smith",
        "payment_methods": [
            {
                "card_id": "card_003",
                "type": "credit",
                "brand": "Chase Freedom Unlimited",
                "last4": "9012",
                "nickname": "Freedom Unlimited"
            }
        ]
    }
}

# Initialize FastMCP server
mcp = FastMCP("SafePayWallet")

class PaymentMethodError(Exception):
    """Custom exception for payment method errors."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

@mcp.tool()
async def get_payment_methods(user_id: str) -> Dict[str, Any]:
    """
    Retrieves the list of available payment methods for a specific user.
    Provides details for each payment method, including card ID, type, brand, last four digits, and nickname.

    Args:
        user_id: The unique identifier (string) for the user whose payment methods are being requested (e.g., 'user1'). This is a required parameter.

    Returns:
        A dictionary containing the user's payment methods.
        - 'payment_methods': A list of dictionaries, where each dictionary represents a payment method with keys like 'card_id', 'type', 'brand', 'last4', and 'nickname'.
        - 'request_id': A unique identifier for this request.
        - 'timestamp': The timestamp when the request was processed.

    Raises:
        PaymentMethodError: If the request fails due to an invalid user ID (user not found) or internal errors.

    Example Conversation:
        User: What payment methods do I have on file?
        Assistant: (Calls get_payment_methods with appropriate parameters like user_id='user1')

    Example Response (simplified):
        {
            "payment_methods": [
                {"card_id": "card_001", "type": "credit", "brand": "Chase Freedom", "last4": "1234", "nickname": "Freedom Card"},
                // ... other payment methods
            ],
            "request_id": "...",
            "timestamp": "..."
        }
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Retrieving payment methods for user: {user_id}")
    
    try:
        if user_id not in MOCK_USERS:
            raise PaymentMethodError(
                f"User {user_id} not found",
                "USER_NOT_FOUND",
                {
                    "invalid_user_id": user_id,
                    "valid_user_ids": list(MOCK_USERS.keys())
                }
            )
            
        payment_methods = MOCK_USERS[user_id]["payment_methods"]
        response = {
            "payment_methods": payment_methods,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[{request_id}] Successfully retrieved {len(payment_methods)} payment methods")
        return response
        
    except PaymentMethodError as e:
        logger.error(f"[{request_id}] Payment method error: {str(e)}", exc_info=True)
        raise PaymentMethodError(
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
        raise PaymentMethodError(
            "An unexpected error occurred while processing the request",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

if __name__ == "__main__":
    logger.info("Starting SafePayWallet MCP server")
    mcp.run() 