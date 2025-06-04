import logging
from typing import List, Dict, Any
import sys
from pathlib import Path
import json
from datetime import datetime

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from mcp.server.fastmcp import FastMCP
from model.card_benefits_request import CardBenefitsRequest
from model.card_benefits_response import CardBenefitsResponse, CardBenefits, Multiplier, Perk

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s'
)
logger = logging.getLogger(__name__)

# Mock card benefits data
MOCK_CARD_BENEFITS = {
    "freedom": {
        "card_id": "freedom",
        "card_name": "Chase Freedom",
        "annual_fee": 0.0,
        "multipliers": [
            {
                "category": "rotating_categories",
                "multiplier": 5.0,
                "description": "5% cash back on up to $1,500 in combined purchases in rotating categories each quarter"
            },
            {
                "category": "all_other_purchases",
                "multiplier": 1.0,
                "description": "1% cash back on all other purchases"
            }
        ],
        "perks": [
            {
                "name": "No Annual Fee",
                "description": "No annual fee",
                "value": 0.0
            }
        ],
        "point_value": 1.0
    },
    "freedom_unlimited": {
        "card_id": "freedom_unlimited",
        "card_name": "Chase Freedom Unlimited",
        "annual_fee": 0.0,
        "multipliers": [
            {
                "category": "all_purchases",
                "multiplier": 1.5,
                "description": "1.5% cash back on all purchases"
            }
        ],
        "perks": [
            {
                "name": "No Annual Fee",
                "description": "No annual fee",
                "value": 0.0
            }
        ],
        "point_value": 1.0
    },
    "sapphire_preferred": {
        "card_id": "sapphire_preferred",
        "card_name": "Chase Sapphire Preferred",
        "annual_fee": 95.0,
        "multipliers": [
            {
                "category": "travel_dining",
                "multiplier": 2.0,
                "description": "2X points on travel and dining at restaurants"
            },
            {
                "category": "all_other_purchases",
                "multiplier": 1.0,
                "description": "1X points on all other purchases"
            }
        ],
        "perks": [
            {
                "name": "Annual Fee",
                "description": "$95 annual fee",
                "value": 95.0
            },
            {
                "name": "Transfer Partners",
                "description": "Transfer points to airline and hotel partners",
                "value": None
            }
        ],
        "point_value": 1.25
    },
    "sapphire_reserve": {
        "card_id": "sapphire_reserve",
        "card_name": "Chase Sapphire Reserve",
        "annual_fee": 550.0,
        "multipliers": [
            {
                "category": "travel_dining",
                "multiplier": 3.0,
                "description": "3X points on travel and dining at restaurants"
            },
            {
                "category": "all_other_purchases",
                "multiplier": 1.0,
                "description": "1X points on all other purchases"
            }
        ],
        "perks": [
            {
                "name": "Annual Fee",
                "description": "$550 annual fee",
                "value": 550.0
            },
            {
                "name": "Travel Credit",
                "description": "$300 annual travel credit",
                "value": 300.0
            },
            {
                "name": "Transfer Partners",
                "description": "Transfer points to airline and hotel partners",
                "value": None
            },
            {
                "name": "Priority Pass",
                "description": "Priority Pass Select membership",
                "value": None
            }
        ],
        "point_value": 1.5
    }
}

# Initialize FastMCP server
mcp = FastMCP("Benefits")

class CardBenefitsError(Exception):
    """Custom exception for card benefits errors."""
    def __init__(self, message: str, error_code: str, details: Dict[str, Any] = None):
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        super().__init__(self.message)

def get_card_benefits_internal(card_ids: List[str]) -> List[Dict[str, Any]]:
    """
    Get benefits for specified cards.
    
    Args:
        card_ids: List of card IDs to get benefits for
        
    Returns:
        List[Dict[str, Any]]: List of card benefits
        
    Raises:
        CardBenefitsError: If any card_id is not found or other errors occur
    """
    logger.info(f"Processing request for card IDs: {card_ids}")
    
    if not card_ids:
        raise CardBenefitsError(
            "No card IDs provided",
            "MISSING_CARD_IDS",
            {"required": "At least one card ID must be provided"}
        )
    
    benefits = []
    invalid_cards = []
    
    for card_id in card_ids:
        if card_id not in MOCK_CARD_BENEFITS:
            invalid_cards.append(card_id)
            logger.warning(f"Card ID not found: {card_id}")
        else:
            benefits.append(MOCK_CARD_BENEFITS[card_id])
            logger.info(f"Found benefits for card: {card_id}")
    
    if invalid_cards:
        raise CardBenefitsError(
            f"Invalid card IDs: {', '.join(invalid_cards)}",
            "INVALID_CARD_IDS",
            {
                "invalid_cards": invalid_cards,
                "valid_cards": list(MOCK_CARD_BENEFITS.keys())
            }
        )
    
    return benefits

async def get_card_benefits(request: CardBenefitsRequest) -> CardBenefitsResponse:
    """
    Get benefits for specified cards.
    
    Args:
        request: The card benefits request containing card IDs
        
    Returns:
        CardBenefitsResponse: The card benefits response
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Received request for card benefits: {request.card_ids}")
    
    try:
        benefits = get_card_benefits_internal(request.card_ids)
        
        response_cards = [
            CardBenefits(
                card_id=benefit["card_id"],
                card_name=benefit["card_name"],
                annual_fee=benefit["annual_fee"],
                multipliers=[
                    Multiplier(**multiplier)
                    for multiplier in benefit["multipliers"]
                ],
                perks=[
                    Perk(**perk)
                    for perk in benefit["perks"]
                ],
                point_value=benefit["point_value"]
            )
            for benefit in benefits
        ]
        
        response = CardBenefitsResponse(cards=response_cards)
        logger.info(f"[{request_id}] Successfully processed request. Found benefits for {len(response_cards)} cards")
        return response
        
    except CardBenefitsError as e:
        logger.error(f"[{request_id}] Card benefits error: {str(e)}", exc_info=True)
        raise CardBenefitsError(
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
        raise CardBenefitsError(
            "An unexpected error occurred while processing the request",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

# Register MCP tool
@mcp.tool()
async def get_card_benefits(card_ids: List[str]) -> Dict[str, Any]:
    """
    Retrieves detailed benefits information for a list of specified credit cards.
    Provides details on annual fees, points multipliers for different categories, card perks, and point value.

    Args:
        card_ids: A list of strings, where each string is the unique identifier (ID) of a credit card (e.g., ['freedom', 'sapphire_preferred']). At least one card ID is required.

    Returns:
        A dictionary containing the benefits information for the requested cards.
        - 'cards': A list of dictionaries, where each dictionary represents a card with keys like 'card_id', 'card_name', 'annual_fee', 'multipliers' (a list of multiplier dictionaries), 'perks' (a list of perk dictionaries), and 'point_value'.

    Raises:
        CardBenefitsError: If the request fails due to invalid input (e.g., missing required card IDs, or if any provided card ID is not found), or internal errors.

    Example Conversation:
        User: What are the benefits of the Chase Sapphire Preferred card?
        Assistant: (Calls get_card_benefits with appropriate parameters like card_ids=['sapphire_preferred'])

    Example Response (simplified):
        {
            "cards": [
                {
                    "card_id": "sapphire_preferred",
                    "card_name": "Chase Sapphire Preferred",
                    "annual_fee": 95.0,
                    "multipliers": [...],
                    "perks": [...],
                    "point_value": 1.25
                }
            ]
        }
    """
    request_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    logger.info(f"[{request_id}] Received request for card benefits: {card_ids}")
    
    try:
        if not card_ids:
            raise CardBenefitsError(
                "No card IDs provided",
                "MISSING_CARD_IDS",
                {"required": "At least one card ID must be provided"}
            )
            
        benefits = []
        for card_id in card_ids:
            if card_id in MOCK_CARD_BENEFITS:
                benefits.append(MOCK_CARD_BENEFITS[card_id])
            else:
                logger.warning(f"[{request_id}] Card not found: {card_id}")
                
        response = {
            "cards": benefits,
            "request_id": request_id,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"[{request_id}] Successfully retrieved benefits for {len(benefits)} cards")
        return response
        
    except CardBenefitsError as e:
        logger.error(f"[{request_id}] Card benefits error: {str(e)}", exc_info=True)
        raise CardBenefitsError(
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
        raise CardBenefitsError(
            "An unexpected error occurred while processing the request",
            "INTERNAL_ERROR",
            {
                "request_id": request_id,
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }
        )

if __name__ == "__main__":
    logger.info("Starting Benefits MCP server")
    mcp.run() 