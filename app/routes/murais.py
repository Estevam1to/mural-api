from typing import Any, Dict, List, Optional

from config.database import get_database
from fastapi import APIRouter, Depends, HTTPException, Query
from models.mural import Mural, MuralCreate, MuralUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.mural_service import MuralService

router = APIRouter(prefix="/murais", tags=["murais"])


async def get_mural_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> MuralService:
    return MuralService(db)


@router.post("/", response_model=dict, status_code=201)
async def criar_mural(
    mural: MuralCreate, service: MuralService = Depends(get_mural_service)
):
    """F1 - Criar mural"""
    try:
        mural_id = await service.create_mural(mural)
        return {"id": mural_id, "message": "Mural criado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=Dict[str, Any])
async def listar_murais(
    bairro: Optional[str] = Query(None, description="Filtrar por bairro"),
    tag: Optional[str] = Query(None, description="Filtrar por tag"),
    artista_id: Optional[str] = Query(None, description="Filtrar por artista"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: MuralService = Depends(get_mural_service),
):
    """F2 - Listar murais com filtros e paginação"""
    return await service.list_murais(
        bairro=bairro, tag=tag, artista_id=artista_id, page=page, limit=limit
    )


@router.get("/count")
async def contar_murais_por_bairro(
    bairro: str = Query(..., description="Nome do bairro"),
    service: MuralService = Depends(get_mural_service),
):
    """F4 - Contagem de murais por bairro"""
    count = await service.count_by_bairro(bairro)
    return {"bairro": bairro, "total_murais": count}


@router.get("/top-artistas", response_model=List[Dict[str, Any]])
async def top_artistas_por_murais(
    limit: int = Query(5, ge=1, le=20, description="Quantidade de artistas"),
    service: MuralService = Depends(get_mural_service),
):
    """F7 - Top artistas com mais murais"""
    return await service.get_top_artistas_by_murais(limit)


@router.get("/media-avaliacao-bairro", response_model=List[Dict[str, Any]])
async def media_avaliacao_por_bairro(
    service: MuralService = Depends(get_mural_service),
):
    """F7 - Média de avaliação por bairro"""
    return await service.get_media_avaliacao_por_bairro()


@router.get("/{mural_id}", response_model=Mural)
async def obter_mural(
    mural_id: str, service: MuralService = Depends(get_mural_service)
):
    """F3 - Obter mural por ID"""
    mural = await service.get_by_id(mural_id)
    if not mural:
        raise HTTPException(status_code=404, detail="Mural não encontrado")
    return mural


@router.put("/{mural_id}", response_model=dict)
async def atualizar_mural(
    mural_id: str,
    mural_data: MuralUpdate,
    service: MuralService = Depends(get_mural_service),
):
    """F3 - Atualizar mural"""
    success = await service.update_mural(mural_id, mural_data)
    if not success:
        raise HTTPException(status_code=404, detail="Mural não encontrado")
    return {"message": "Mural atualizado com sucesso"}


@router.delete("/{mural_id}", response_model=dict)
async def deletar_mural(
    mural_id: str, service: MuralService = Depends(get_mural_service)
):
    """F3 - Deletar mural"""
    success = await service.delete(mural_id)
    if not success:
        raise HTTPException(status_code=404, detail="Mural não encontrado")
    return {"message": "Mural deletado com sucesso"}
