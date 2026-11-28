"""Testes unitários das operações CRUD de produtos (app/routers/produtos.py).

Dublês de teste utilizados:
- Fake (FakeSession): simula em memória o armazenamento e controle de ids/commits.
- Stub/Mock (unittest.mock.Mock): simula retorno nulo (`db.get`) para validar erros 404
  e verifica que `commit` não é chamado em falhas.
"""

from decimal import Decimal
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app import models, schemas
from app.routers import produtos as rotas


class FakeSession:
    """Fake em memória para simular sessão/persistência de Produto."""

    def __init__(self, produtos: list[models.Produto] | None = None):
        self.dados: dict[int, models.Produto] = {}
        self._proximo_id = 1
        self.commits = 0
        self.refreshes = 0
        self.deletes: list[models.Produto] = []

        for p in produtos or []:
            if p.id is None:
                p.id = self._proximo_id
                self._proximo_id += 1
            else:
                self._proximo_id = max(self._proximo_id, p.id + 1)
            self.dados[p.id] = p

    def get(self, model, obj_id: int):
        if model is not models.Produto:
            return None
        return self.dados.get(obj_id)

    def add(self, obj: models.Produto):
        if obj.id is None:
            obj.id = self._proximo_id
            self._proximo_id += 1
        self.dados[obj.id] = obj

    def commit(self):
        self.commits += 1

    def refresh(self, obj: models.Produto):
        self.refreshes += 1
        if obj.id is not None:
            self.dados[obj.id] = obj

    def delete(self, obj: models.Produto):
        self.deletes.append(obj)
        self.dados.pop(obj.id, None)


def test_criar_produto_atribui_id_e_persiste():
    fake_db = FakeSession()
    payload = schemas.ProdutoCreate(
        nome="Caderno 10 matérias",
        descricao="Capa dura",
        preco=Decimal("24.90"),
        quantidade=12,
    )

    criado = rotas.criar(payload, fake_db)

    assert criado.id == 1
    assert criado.nome == "Caderno 10 matérias"
    assert criado.quantidade == 12
    assert fake_db.commits == 1
    assert fake_db.refreshes == 1


def test_obter_produto_inexistente_lanca_404():
    db = Mock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        rotas.obter(999, db)

    assert exc.value.status_code == 404
    assert exc.value.detail == "Produto não encontrado"
    db.commit.assert_not_called()


def test_atualizar_produto_parcial_altera_apenas_campos_enviados():
    produto = models.Produto(
        id=2,
        nome="Mouse USB",
        descricao="Óptico",
        preco=Decimal("45.00"),
        quantidade=8,
    )
    fake_db = FakeSession([produto])
    payload = schemas.ProdutoUpdate(preco=Decimal("49.90"))

    atualizado = rotas.atualizar(2, payload, fake_db)

    assert atualizado.preco == Decimal("49.90")
    assert atualizado.nome == "Mouse USB"
    assert atualizado.descricao == "Óptico"
    assert atualizado.quantidade == 8
    assert fake_db.commits == 1


def test_atualizar_produto_inexistente_lanca_404():
    db = Mock()
    db.get.return_value = None

    with pytest.raises(HTTPException) as exc:
        rotas.atualizar(404, schemas.ProdutoUpdate(nome="Novo"), db)

    assert exc.value.status_code == 404
    db.commit.assert_not_called()


def test_remover_produto_existente_chama_delete_e_commit():
    produto = models.Produto(
        id=3,
        nome="Teclado",
        descricao=None,
        preco=Decimal("80.00"),
        quantidade=2,
    )
    fake_db = FakeSession([produto])

    rotas.remover(3, fake_db)

    assert len(fake_db.deletes) == 1
    assert fake_db.deletes[0].id == 3
    assert fake_db.get(models.Produto, 3) is None
    assert fake_db.commits == 1