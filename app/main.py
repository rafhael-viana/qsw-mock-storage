from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database import Base, engine
from app.routers import produtos


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Cria as tabelas na inicialização (simples; para algo maior, usar Alembic)
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="Estoque", lifespan=lifespan)
app.include_router(produtos.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok"}
