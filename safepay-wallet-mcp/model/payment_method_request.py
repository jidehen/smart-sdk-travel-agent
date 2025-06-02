from pydantic import BaseModel

class PaymentMethodRequest(BaseModel):
    user_id: str 