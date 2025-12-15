from datetime import datetime
from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    Boolean,
    Float,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Network(Base):
    __tablename__ = "networks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    native_symbol = Column(String, nullable=False)
    is_token = Column(Boolean, default=False)
    parent_chain = Column(String, nullable=True)


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    network_code = Column(String, nullable=False, index=True)
    tx_hash = Column(String, nullable=False, index=True)
    signed_tx = Column(String, nullable=False)
    status = Column(String, nullable=False, default="pending")
    to_address = Column(String, nullable=True)
    from_address = Column(String, nullable=True)
    amount = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User")


class P2POrder(Base):
    __tablename__ = "p2p_orders"

    id = Column(Integer, primary_key=True, index=True)
    maker_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    taker_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    side = Column(String, nullable=False)  # 'buy' / 'sell'
    fiat_currency = Column(String, nullable=False)
    crypto_currency = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    price = Column(Float, nullable=False)

    status = Column(String, nullable=False, default="active")
    maker_confirmed = Column(Boolean, default=False)
    taker_confirmed = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    maker = relationship("User", foreign_keys=[maker_id])
    taker = relationship("User", foreign_keys=[taker_id])
