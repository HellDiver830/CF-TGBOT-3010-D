import re
from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class AddressValidateIn(BaseModel):
    network: str
    address: str


class AddressValidateOut(BaseModel):
    is_valid: bool


BTC_RE = re.compile(r"^(bc1|[13])[a-zA-HJ-NP-Z0-9]{25,39}$")
ETH_RE = re.compile(r"^0x[a-fA-F0-9]{40}$")
TRON_RE = re.compile(r"^T[1-9A-HJ-NP-Za-km-z]{33}$")
TON_RE = re.compile(r"^((EQ|UQ)[a-zA-Z0-9_-]{48})$")


@router.post("/address/validate", response_model=AddressValidateOut)
def validate_address(payload: AddressValidateIn):
    net = payload.network.upper()
    addr = payload.address.strip()

    valid = False
    if net in {"BTC", "LTC"}:
        valid = bool(BTC_RE.match(addr))
    elif net in {"ETH", "USDT_ERC20", "BNB"}:
        valid = bool(ETH_RE.match(addr))
    elif net in {"TRX", "USDT_TRC20"}:
        valid = bool(TRON_RE.match(addr))
    elif net == "TON":
        valid = bool(TON_RE.match(addr))

    return AddressValidateOut(is_valid=valid)
