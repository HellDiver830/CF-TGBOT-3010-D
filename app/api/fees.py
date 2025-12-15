from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class FeeEstimateIn(BaseModel):
    network: str
    amount: float


class FeeEstimateOut(BaseModel):
    network: str
    amount: float
    fee: float


BASE_FEES = {
    "BTC": 0.00005,
    "LTC": 0.0005,
    "ETH": 0.0005,
    "USDT_ERC20": 3.0,
    "BNB": 0.0003,
    "TRX": 1.0,
    "USDT_TRC20": 1.5,
    "TON": 0.02,
}


@router.post("/fees/estimate", response_model=FeeEstimateOut)
def estimate_fee(payload: FeeEstimateIn):
    net = payload.network.upper()
    base_fee = BASE_FEES.get(net, 0.001)
    # Примитивная модель: комиссия пропорциональна логарифму суммы
    fee = base_fee * (1.0 + 0.1 * (len(str(int(payload.amount))) if payload.amount > 0 else 0))
    return FeeEstimateOut(network=net, amount=payload.amount, fee=fee)
