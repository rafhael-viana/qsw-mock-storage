"""Testes unitários das regras de estoque (app/routers/produtos.py).

As funções das rotas são chamadas diretamente, sem servidor HTTP e sem banco
de dados, então os testes rodam em memória, rápidos e determinísticos.

Dublês de teste utilizados (unittest.mock):
- Stub: a sessão do banco tem `db.get` configurado para devolver um produto
  preparado no próprio teste (ou None), isolando a regra do PostgreSQL.
- Mock/Spy: a mesma sessão registra as chamadas a `commit`, `refresh` e
  `delete`, e o teste verifica se o código persistiu (ou não) a alteração.
"""

from decimal import Decimal
from unittest.mock import Mock

import pytest
from fastapi import HTTPException

from app import models, schemas
from app.routers import produtos as rotas


def criar_produto(quantidade: int = 5) -> models.Produto:
    return models.Produto(
        id=1,
        nome="Caneta azul",
        descricao=None,
        preco=Decimal("2.50"),
        quantidade=quantidade,
    )


def sessao_stub(produto: models.Produto | None) -> Mock:
    """Sessão falsa: `get` sempre devolve o produto informado (Stub) e
    todas as outras chamadas ficam registradas para verificação (Mock)."""
    db = Mock()
    db.get.return_value = produto
    return db


def test_saida_maior_que_estoque_lanca_400_e_nao_persiste():
    """Stub devolve produto com 5 unidades; Mock garante que nada foi gravado."""
    produto = criar_produto(quantidade=5)
    db = sessao_stub(produto)

    with pytest.raises(HTTPException) as erro:
        rotas.saida(1, schemas.Movimentacao(quantidade=6), db)

    assert erro.value.status_code == 400
    assert erro.value.detail == "Estoque insuficiente"
    assert produto.quantidade == 5
    db.commit.assert_not_called()


def test_saida_valida_diminui_quantidade_e_persiste():
    """Mock verifica que a saída válida foi gravada exatamente uma vez."""
    produto = criar_produto(quantidade=5)
    db = sessao_stub(produto)

    resultado = rotas.saida(1, schemas.Movimentacao(quantidade=3), db)

    assert resultado.quantidade == 2
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(produto)


def test_saida_de_todo_o_estoque_zera_quantidade():
    """Valor-limite: retirar exatamente o que existe é permitido."""
    produto = criar_produto(quantidade=4)
    db = sessao_stub(produto)

    resultado = rotas.saida(1, schemas.Movimentacao(quantidade=4), db)

    assert resultado.quantidade == 0
    db.commit.assert_called_once()


def test_entrada_soma_quantidade_e_persiste():
    produto = criar_produto(quantidade=5)
    db = sessao_stub(produto)

    resultado = rotas.entrada(1, schemas.Movimentacao(quantidade=10), db)

    assert resultado.quantidade == 15
    db.commit.assert_called_once()


def test_movimentar_produto_inexistente_lanca_404():
    """Stub devolve None, simulando um id que não existe no banco."""
    db = sessao_stub(None)

    with pytest.raises(HTTPException) as erro:
        rotas.saida(99, schemas.Movimentacao(quantidade=1), db)

    assert erro.value.status_code == 404
    db.get.assert_called_once_with(models.Produto, 99)
    db.commit.assert_not_called()
