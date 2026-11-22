from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

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


# Interface web (HTML/JS estático) servida em /ui
STATIC_DIR = Path(__file__).parent / "static"
app.mount("/ui", StaticFiles(directory=STATIC_DIR, html=True), name="ui")


@app.get("/", include_in_schema=False)
def raiz():
    return RedirectResponse("/ui/")
