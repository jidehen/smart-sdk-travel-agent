from pydantic import BaseModel

class PaymentMethodResponse(BaseModel):
    card_id: str
    type: str
    brand: str
    last4: str
    nickname: str 