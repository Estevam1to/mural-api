from typing import List

from config.database import get_database
from fastapi import APIRouter, Depends, HTTPException, Query
from models.artista import Artista, ArtistaCreate, ArtistaUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.artista_service import ArtistaService

router = APIRouter(prefix="/artistas", tags=["artistas"])


async def get_artista_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> ArtistaService:
    return ArtistaService(db)


@router.post("/", response_model=dict, status_code=201)
async def criar_artista(
    artista: ArtistaCreate, service: ArtistaService = Depends(get_artista_service)
):
    """Criar novo artista"""
    try:
        artista_id = await service.create_artista(artista)
        return {"id": artista_id, "message": "Artista criado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=dict)
async def listar_artistas(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: ArtistaService = Depends(get_artista_service),
):
    """Listar artistas com paginação"""
    return await service.list_with_pagination(page=page, limit=limit)


@router.get("/search", response_model=List[Artista])
async def buscar_artistas_por_nome(
    nome: str = Query(..., description="Nome do artista"),
    service: ArtistaService = Depends(get_artista_service),
):
    """Buscar artistas por nome"""
    return await service.search_by_name(nome)


@router.get("/{artista_id}", response_model=Artista)
async def obter_artista(
    artista_id: str, service: ArtistaService = Depends(get_artista_service)
):
    """Obter artista por ID"""
    artista = await service.get_by_id(artista_id)
    if not artista:
        raise HTTPException(status_code=404, detail="Artista não encontrado")
    return artista


@router.put("/{artista_id}", response_model=dict)
async def atualizar_artista(
    artista_id: str,
    artista_data: ArtistaUpdate,
    service: ArtistaService = Depends(get_artista_service),
):
    """Atualizar artista"""
    success = await service.update_artista(artista_id, artista_data)
    if not success:
        raise HTTPException(status_code=404, detail="Artista não encontrado")
    return {"message": "Artista atualizado com sucesso"}


@router.delete("/{artista_id}", response_model=dict)
async def deletar_artista(
    artista_id: str, service: ArtistaService = Depends(get_artista_service)
):
    """Deletar artista"""
    success = await service.delete(artista_id)
    if not success:
        raise HTTPException(status_code=404, detail="Artista não encontrado")
    return {"message": "Artista deletado com sucesso"}
