from pydantic import BaseModel, ConfigDict


class NetworkOut(BaseModel):
    code: str
    name: str
    native_symbol: str
    is_token: bool
    parent_chain: str | None = None

    model_config = ConfigDict(from_attributes=True)
