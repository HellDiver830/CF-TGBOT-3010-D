from app.db import Base, engine, SessionLocal
from app import models


def init_db() -> None:
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        networks = [
            {
                "code": "BTC",
                "name": "Bitcoin",
                "native_symbol": "BTC",
                "is_token": False,
                "parent_chain": None,
            },
            {
                "code": "ETH",
                "name": "Ethereum",
                "native_symbol": "ETH",
                "is_token": False,
                "parent_chain": None,
            },
            {
                "code": "USDT_ERC20",
                "name": "Tether USD (ERC20)",
                "native_symbol": "USDT",
                "is_token": True,
                "parent_chain": "ETH",
            },
            {
                "code": "TRX",
                "name": "TRON",
                "native_symbol": "TRX",
                "is_token": False,
                "parent_chain": None,
            },
            {
                "code": "USDT_TRC20",
                "name": "Tether USD (TRC20)",
                "native_symbol": "USDT",
                "is_token": True,
                "parent_chain": "TRX",
            },
            {
                "code": "LTC",
                "name": "Litecoin",
                "native_symbol": "LTC",
                "is_token": False,
                "parent_chain": None,
            },
            {
                "code": "BNB",
                "name": "BNB Smart Chain",
                "native_symbol": "BNB",
                "is_token": False,
                "parent_chain": None,
            },
            {
                "code": "TON",
                "name": "The Open Network",
                "native_symbol": "TON",
                "is_token": False,
                "parent_chain": None,
            },
        ]

        for n in networks:
            existing = db.query(models.Network).filter(models.Network.code == n["code"]).first()
            if not existing:
                db.add(models.Network(**n))

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    init_db()
    print("DB initialized.")
