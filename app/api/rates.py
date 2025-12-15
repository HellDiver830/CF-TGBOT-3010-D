from fastapi import APIRouter, HTTPException
from app.services.rates_cache import rates_cache

router = APIRouter()


@router.get("/rates")
async def get_rates():
    try:
        data = await rates_cache.get_rates()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Не удалось получить курсы: {exc}")
    return data
