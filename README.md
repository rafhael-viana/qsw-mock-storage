# Estoque

API simples de estoque com FastAPI + PostgreSQL.

## Rodando com Docker

```bash
docker compose up --build
```

- API: http://localhost:8000 (mude a porta com `API_PORT=8001 docker compose up`)
- Documentação (Swagger): http://localhost:8000/docs

## Rodando localmente

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
docker compose up -d db          # sobe só o Postgres
uvicorn app.main:app --reload
```

## Testes

```bash
pytest
```

## Endpoints

| Método | Rota                         | Descrição               |
|--------|------------------------------|-------------------------|
| GET    | `/health`                    | Health check            |
| GET    | `/produtos`                  | Lista produtos          |
| GET    | `/produtos/{id}`             | Detalha produto         |
| POST   | `/produtos`                  | Cria produto            |
| PATCH  | `/produtos/{id}`             | Atualiza produto        |
| DELETE | `/produtos/{id}`             | Remove produto          |
| POST   | `/produtos/{id}/entrada`     | Entrada no estoque      |
| POST   | `/produtos/{id}/saida`       | Saída do estoque        |
