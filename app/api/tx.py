from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.schemas.tx import TxBroadcastIn, TxOut
from app.services.security import get_current_user
from app.services import tatum_client
from app.core.config import settings

router = APIRouter()


@router.post("/tx/broadcast", response_model=TxOut)
async def broadcast_tx(
    payload: TxBroadcastIn,
    db: Session = Depends(get_db),
    current_user: models.User | None = Depends(get_current_user),
):
    net = payload.network.upper()

    # Проверяем, что сеть есть в справочнике
    network = db.query(models.Network).filter(models.Network.code == net).first()
    if not network:
        raise HTTPException(status_code=400, detail=f"Неизвестная сеть: {net}")

    # Пытаемся отправить транзакцию в Tatum, если он настроен
    if settings.tatum_api_key:
        try:
            tx_hash = await tatum_client.broadcast_signed_tx(net, payload.signed_tx)
            status = "pending"
        except tatum_client.TatumNotConfigured:
            tx_hash = payload.signed_tx  # fallback
            status = "pending"
        except HTTPException as exc:
            raise exc
        except Exception as exc:
            # На всякий случай не скрываем ошибку
            raise HTTPException(status_code=502, detail=f"Tatum error: {exc}")
    else:
        # Если Tatum не настроен, оставляем поведение как у тестового стенда
        # и используем псевдо-хеш
        import hashlib
        tx_hash = hashlib.sha256(payload.signed_tx.encode()).hexdigest()
        status = "pending"

    tx = models.Transaction(
        user_id=current_user.id if current_user else None,
        network_code=net,
        tx_hash=tx_hash,
        signed_tx=payload.signed_tx,
        to_address=payload.to_address,
        from_address=payload.from_address,
        amount=payload.amount,
        status=status,
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)

    return TxOut(network=net, tx_hash=tx_hash, status=status)


@router.get("/tx/{network}/{tx_hash}", response_model=TxOut)
async def get_tx_status(
    network: str,
    tx_hash: str,
    db: Session = Depends(get_db),
):
    net = network.upper()
    tx = (
        db.query(models.Transaction)
        .filter(models.Transaction.network_code == net, models.Transaction.tx_hash == tx_hash)
        .first()
    )
    if not tx:
        # Даже если в БД нет, можем попробовать спросить у Tatum
        if settings.tatum_api_key:
            chain_status = await tatum_client.get_tx_status(net, tx_hash)
            return TxOut(network=net, tx_hash=tx_hash, status=chain_status)
        raise HTTPException(status_code=404, detail="Транзакция не найдена")

    status = tx.status

    if settings.tatum_api_key:
        try:
            chain_status = await tatum_client.get_tx_status(net, tx_hash)
            # Обновляем статус, если он изменился
            if chain_status and chain_status != tx.status:
                tx.status = chain_status
                db.commit()
                db.refresh(tx)
            status = tx.status
        except Exception:
            # В боевом коде логировалось бы в Sentry/лог, но API не ломаем
            pass

    return TxOut(network=net, tx_hash=tx_hash, status=status)
