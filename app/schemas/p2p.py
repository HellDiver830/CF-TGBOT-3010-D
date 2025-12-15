from datetime import datetime
from pydantic import BaseModel, ConfigDict


class P2POrderCreate(BaseModel):
    side: str
    fiat_currency: str
    crypto_currency: str
    amount: float
    price: float


class P2POrderOut(BaseModel):
    id: int
    side: str
    fiat_currency: str
    crypto_currency: str
    amount: float
    price: float
    status: str
    maker_id: int
    taker_id: int | None
    maker_confirmed: bool
    taker_confirmed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
