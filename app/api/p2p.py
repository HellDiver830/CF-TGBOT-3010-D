from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.schemas.p2p import P2POrderCreate, P2POrderOut
from app.services.security import get_current_user

router = APIRouter()


@router.post("/orders", response_model=P2POrderOut)
def create_order(
    payload: P2POrderCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    if payload.side not in {"buy", "sell"}:
        raise HTTPException(status_code=400, detail="side должен быть 'buy' или 'sell'")

    order = models.P2POrder(
        maker_id=current_user.id,
        side=payload.side,
        fiat_currency=payload.fiat_currency.upper(),
        crypto_currency=payload.crypto_currency.upper(),
        amount=payload.amount,
        price=payload.price,
        status="active",
    )
    db.add(order)
    db.commit()
    db.refresh(order)
    return order


@router.get("/orders", response_model=list[P2POrderOut])
def list_active_orders(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    # Показываем активные ордера, созданные другими пользователями
    orders = (
        db.query(models.P2POrder)
        .filter(models.P2POrder.status == "active", models.P2POrder.maker_id != current_user.id)
        .order_by(models.P2POrder.id)
        .all()
    )
    return orders


@router.post("/orders/{order_id}/accept", response_model=P2POrderOut)
def accept_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.P2POrder).filter(models.P2POrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    if order.maker_id == current_user.id:
        raise HTTPException(status_code=400, detail="Нельзя принять собственный ордер")
    if order.status != "active":
        raise HTTPException(status_code=400, detail=f"Нельзя принять ордер со статусом {order.status}")
    if order.taker_id is not None:
        raise HTTPException(status_code=400, detail="Ордер уже принят")

    order.taker_id = current_user.id
    order.status = "in_progress"
    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/{order_id}/confirm", response_model=P2POrderOut)
def confirm_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.P2POrder).filter(models.P2POrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    if order.status not in {"in_progress", "active"}:
        raise HTTPException(status_code=400, detail=f"Нельзя подтвердить ордер со статусом {order.status}")
    if current_user.id not in {order.maker_id, order.taker_id}:
        raise HTTPException(status_code=403, detail="Вы не участвуете в этой сделке")

    if current_user.id == order.maker_id:
        order.maker_confirmed = True
    if current_user.id == order.taker_id:
        order.taker_confirmed = True

    # Если обе стороны подтвердили – считаем сделку завершённой
    if order.maker_confirmed and order.taker_confirmed and order.taker_id is not None:
        order.status = "completed"
    else:
        # Иначе оставляем 'in_progress'
        order.status = "in_progress"

    db.commit()
    db.refresh(order)
    return order


@router.post("/orders/{order_id}/cancel", response_model=P2POrderOut)
def cancel_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    order = db.query(models.P2POrder).filter(models.P2POrder.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Ордер не найден")
    if order.maker_id != current_user.id:
        raise HTTPException(status_code=403, detail="Отменять может только создатель ордера")
    if order.status in {"completed", "cancelled"}:
        raise HTTPException(status_code=400, detail=f"Нельзя отменить ордер со статусом {order.status}")

    order.status = "cancelled"
    db.commit()
    db.refresh(order)
    return order


@router.get("/history", response_model=list[P2POrderOut])
def list_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_user),
):
    orders = (
        db.query(models.P2POrder)
        .filter(
            (models.P2POrder.maker_id == current_user.id)
            | (models.P2POrder.taker_id == current_user.id)
        )
        .order_by(models.P2POrder.id.desc())
        .all()
    )
    return orders
