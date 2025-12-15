from datetime import datetime, timedelta
from typing import Dict, Any
import httpx

from app.core.config import settings


class RatesCache:
    def __init__(self, ttl_seconds: int = 60):
        self.ttl = timedelta(seconds=ttl_seconds)
        self._data: Dict[str, Any] = {}
        self._ts: datetime | None = None

    async def get_rates(self) -> Dict[str, Any]:
        now = datetime.utcnow()
        if self._ts and now - self._ts < self.ttl:
            return self._data

        ids = "bitcoin,ethereum,binancecoin,tether,tron,litecoin,toncoin"
        vs = "usd"
        url = f"{settings.coingecko_base_url}/simple/price"
        params = {"ids": ids, "vs_currencies": vs}

        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        self._data = data
        self._ts = now
        return data


rates_cache = RatesCache()
