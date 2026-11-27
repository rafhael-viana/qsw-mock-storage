
"""Teste unitário de movimentações consecutivas de estoque.

Verifica a consistência do estoque após operações de entrada
e saída, utilizando Stub e Mock para simular o banco de dados.
"""

from decimal import Decimal
from unittest.mock import Mock

from app import models, schemas
from app.routers import produtos as rotas


def test_entrada_seguida_de_saida_atualiza_estoque():
    """Verifica o saldo após movimentações consecutivas."""

    # Arrange: prepara o cenário de teste.
    produto = models.Produto(
        id=1,
        nome="Caneta azul",
        descricao=None,
        preco=Decimal("2.50"),
        quantidade=10,
    )

    db = Mock()
    db.get.return_value = produto

    # Act: realiza uma entrada de cinco unidades.
    rotas.entrada(
        1, schemas.Movimentacao(quantidade=5), db
    )

    assert produto.quantidade == 15

    # Act: realiza uma saída de três unidades.
    resultado = rotas.saida(
        1, schemas.Movimentacao(quantidade=3), db
    )

    # Assert: verifica os resultados.
    assert resultado.quantidade == 12
    assert db.commit.call_count == 2
    assert db.refresh.call_count == 2
