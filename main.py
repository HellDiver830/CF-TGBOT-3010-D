from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

from app.api import auth, networks, rates, address, fees, tx, p2p

app = FastAPI(
    title="Crypto P2P API",
    version="1.0.0",
    description=(
        "Бэкенд для криптокошелька и P2P-платформы без хранения приватных ключей. "
        "Транзакции отправляются во внешние RPC-провайдеры (например, Tatum)."
    ),
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(networks.router, prefix=settings.API_V1_STR)
app.include_router(rates.router, prefix=settings.API_V1_STR)
app.include_router(address.router, prefix=settings.API_V1_STR)
app.include_router(fees.router, prefix=settings.API_V1_STR)
app.include_router(tx.router, prefix=settings.API_V1_STR)
app.include_router(p2p.router, prefix=settings.API_V1_STR)


@app.get("/")
def read_root():
    return {"status": "ok", "message": "Crypto P2P API is running"}
