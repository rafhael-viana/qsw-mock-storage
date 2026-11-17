from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class ProdutoBase(BaseModel):
    nome: str = Field(min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    preco: Decimal = Field(ge=0, decimal_places=2)
    quantidade: int = Field(default=0, ge=0)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: str | None = Field(default=None, min_length=1, max_length=120)
    descricao: str | None = Field(default=None, max_length=500)
    preco: Decimal | None = Field(default=None, ge=0, decimal_places=2)
    quantidade: int | None = Field(default=None, ge=0)


class ProdutoOut(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class Movimentacao(BaseModel):
    quantidade: int = Field(gt=0)
