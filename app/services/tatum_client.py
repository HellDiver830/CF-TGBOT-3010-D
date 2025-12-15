from __future__ import annotations

from typing import Literal

import httpx
from fastapi import HTTPException

from app.core.config import settings

SupportedNetwork = Literal[
    "BTC",
    "LTC",
    "ETH",
    "USDT_ERC20",
    "BNB",
    "TRX",
    "USDT_TRC20",
    "TON",
]


class TatumNotConfigured(Exception):
    pass


def _require_tatum():
    if not settings.tatum_api_key:
        raise TatumNotConfigured("TATUM_API_KEY не задан, интеграция с Tatum отключена")


def _chain_from_network(network: str) -> str:
    n = network.upper()
    if n in {"BTC"}:
        return "bitcoin"
    if n in {"LTC"}:
        return "litecoin"
    if n in {"ETH", "USDT_ERC20"}:
        return "ethereum"
    if n in {"BNB"}:
        return "bsc"
    if n in {"TRX", "USDT_TRC20"}:
        return "tron"
    if n in {"TON"}:
        return "ton"
    raise ValueError(f"Unsupported network for Tatum: {network}")


async def broadcast_signed_tx(network: str, signed_tx: str) -> str:
    """Отправить уже подписанную транзакцию в Tatum.

    Для UTXO-сетей (BTC/LTC) используется /v3/bitcoin|litecoin/broadcast с txData.
    Для EVM (ETH/BNB) и Tron/TON используются соответствующие *broadcast*-эндпоинты.
    См. актуальную документацию Tatum для точных путей и полей.
    """
    _require_tatum()
    chain = _chain_from_network(network)
    base = settings.tatum_base_url.rstrip("/")

    # Подбираем endpoint по chain
    if chain in {"bitcoin", "litecoin"}:
        path = f"/v3/{chain}/broadcast"
        payload = {"txData": signed_tx}
    elif chain in {"ethereum", "bsc"}:
        path = f"/v3/{chain}/broadcast"
        payload = {"txData": signed_tx}
    elif chain == "tron":
        path = "/v3/tron/broadcast"
        payload = {"txData": signed_tx}
    elif chain == "ton":
        # В Tatum есть HTTP API V2 для TON, здесь используем универсальный broadcast-стиль.
        path = "/v3/ton/broadcast"
        payload = {"txData": signed_tx}
    else:
        raise ValueError(f"Unsupported chain: {chain}")

    headers = {"x-api-key": settings.tatum_api_key}

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.post(f"{base}{path}", json=payload, headers=headers)
        if resp.status_code >= 400:
            try:
                detail = resp.json()
            except Exception:
                detail = resp.text
            raise HTTPException(status_code=502, detail={"tatum_error": detail})
        data = resp.json()

    # В большинстве эндпоинтов Tatum хеш транзакции лежит в поле txId или txHash
    tx_hash = data.get("txId") or data.get("txHash") or data.get("hash")
    if not tx_hash:
        # Если Tatum вернул что-то своё, пробрасываем целиком
        raise HTTPException(status_code=502, detail={"tatum_response": data})
    return tx_hash


async def get_tx_status(network: str, tx_hash: str) -> str:
    """Получить статус транзакции через Tatum.

    Здесь мы используем простую эвристику:
    - если транзакция найдена и помечена как успешная -> confirmed
    - если найдена, но с ошибкой/failed -> failed
    - если не найдена -> pending

    Точные эндпоинты и поля зависят от конкретной сети, этот код можно
    детализировать под требования продакшена.
    """
    _require_tatum()
    chain = _chain_from_network(network)
    base = settings.tatum_base_url.rstrip("/")
    headers = {"x-api-key": settings.tatum_api_key}

    # Простейший вариант: использовать /v3/{chain}/transaction/{hash} где доступно.
    if chain in {"bitcoin", "litecoin"}:
        path = f"/v3/{chain}/transaction/{tx_hash}"
    elif chain in {"ethereum", "bsc"}:
        path = f"/v3/{chain}/transaction/{tx_hash}"
    elif chain == "tron":
        path = f"/v3/tron/transaction/{tx_hash}"
    elif chain == "ton":
        path = f"/v3/ton/transaction/{tx_hash}"
    else:
        raise ValueError(f"Unsupported chain: {chain}")

    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(f"{base}{path}", headers=headers)
        if resp.status_code == 404:
            return "pending"
        if resp.status_code >= 400:
            # В спорных случаях не ломаем API, просто оставляем pending
            return "pending"
        data = resp.json()

    # Очень грубая нормализация статуса
    status = "pending"
    # EVM / Tron / TON обычно имеют поле status/txStatus/receipt.success и т.п.
    for key in ("status", "txStatus", "blockStatus", "executionResult"):
        v = data.get(key)
        if isinstance(v, str):
            lv = v.lower()
            if "success" in lv or lv == "ok" or lv == "confirmed":
                status = "confirmed"
                break
            if "fail" in lv or "revert" in lv or lv == "failed":
                status = "failed"
                break

    return status
