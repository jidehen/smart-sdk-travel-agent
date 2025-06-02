from typing import List
from pydantic import BaseModel

class CardBenefitsRequest(BaseModel):
    """Request model for getting card benefits."""
    card_ids: List[str] 