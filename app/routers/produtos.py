from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db

router = APIRouter(prefix="/produtos", tags=["produtos"])


def _get_or_404(db: Session, produto_id: int) -> models.Produto:
    produto = db.get(models.Produto, produto_id)
    if produto is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Produto não encontrado")
    return produto


@router.get("", response_model=list[schemas.ProdutoOut])
def listar(db: Session = Depends(get_db)):
    return db.scalars(select(models.Produto).order_by(models.Produto.id)).all()


@router.get("/{produto_id}", response_model=schemas.ProdutoOut)
def obter(produto_id: int, db: Session = Depends(get_db)):
    return _get_or_404(db, produto_id)


@router.post("", response_model=schemas.ProdutoOut, status_code=status.HTTP_201_CREATED)
def criar(dados: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    produto = models.Produto(**dados.model_dump())
    db.add(produto)
    db.commit()
    db.refresh(produto)
    return produto


@router.patch("/{produto_id}", response_model=schemas.ProdutoOut)
def atualizar(produto_id: int, dados: schemas.ProdutoUpdate, db: Session = Depends(get_db)):
    produto = _get_or_404(db, produto_id)
    for campo, valor in dados.model_dump(exclude_unset=True).items():
        setattr(produto, campo, valor)
    db.commit()
    db.refresh(produto)
    return produto


@router.delete("/{produto_id}", status_code=status.HTTP_204_NO_CONTENT)
def remover(produto_id: int, db: Session = Depends(get_db)):
    produto = _get_or_404(db, produto_id)
    db.delete(produto)
    db.commit()


@router.post("/{produto_id}/entrada", response_model=schemas.ProdutoOut)
def entrada(produto_id: int, mov: schemas.Movimentacao, db: Session = Depends(get_db)):
    produto = _get_or_404(db, produto_id)
    produto.quantidade += mov.quantidade
    db.commit()
    db.refresh(produto)
    return produto


@router.post("/{produto_id}/saida", response_model=schemas.ProdutoOut)
def saida(produto_id: int, mov: schemas.Movimentacao, db: Session = Depends(get_db)):
    produto = _get_or_404(db, produto_id)
    if produto.quantidade < mov.quantidade:
        raise HTTPException(status.HTTP_400_BAD_REQUEST, "Estoque insuficiente")
    produto.quantidade -= mov.quantidade
    db.commit()
    db.refresh(produto)
    return produto
