from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db import get_db
from app import models
from app.schemas.network import NetworkOut

router = APIRouter()


@router.get("/networks", response_model=list[NetworkOut])
def list_networks(db: Session = Depends(get_db)):
    nets = db.query(models.Network).order_by(models.Network.id).all()
    return nets
