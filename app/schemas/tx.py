from pydantic import BaseModel, ConfigDict


class TxBroadcastIn(BaseModel):
    network: str
    signed_tx: str
    to_address: str | None = None
    from_address: str | None = None
    amount: float | None = None


class TxOut(BaseModel):
    network: str
    tx_hash: str
    status: str

    model_config = ConfigDict(from_attributes=True)
