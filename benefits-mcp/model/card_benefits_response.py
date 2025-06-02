from typing import List, Dict, Optional
from pydantic import BaseModel

class Multiplier(BaseModel):
    """Model for reward multipliers."""
    category: str
    multiplier: float
    description: str

class Perk(BaseModel):
    """Model for card perks."""
    name: str
    description: str
    value: Optional[float] = None

class CardBenefits(BaseModel):
    """Model for card benefits."""
    card_id: str
    card_name: str
    annual_fee: float
    multipliers: List[Multiplier]
    perks: List[Perk]
    point_value: float

class CardBenefitsResponse(BaseModel):
    """Response model for card benefits."""
    cards: List[CardBenefits] 