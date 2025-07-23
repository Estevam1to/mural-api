from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorDatabase

from config.database import get_database
from models.avaliacao import Avaliacao, AvaliacaoCreate, AvaliacaoUpdate
from services.avaliacao_service import AvaliacaoService

router = APIRouter(prefix="/avaliacoes", tags=["avaliacoes"])


async def get_avaliacao_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> AvaliacaoService:
    return AvaliacaoService(db)


@router.post("/", response_model=dict)
async def create_avaliacao(
    avaliacao: AvaliacaoCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Criar uma nova avaliação"""
    try:
        service = AvaliacaoService(db)
        result = await service.create_avaliacao(avaliacao)
        return result  # Return directly, not wrapped
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=dict)
async def listar_avaliacoes(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    """Listar avaliações com paginação"""
    return await service.list_with_pagination(page=page, limit=limit)


@router.get("/mural/{mural_id}", response_model=dict)
async def listar_avaliacoes_mural(
    mural_id: str,
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    """Listar avaliações de um mural"""
    return await service.get_by_mural(mural_id, page, limit)


@router.get("/usuario/{usuario_id}", response_model=dict)
async def listar_avaliacoes_usuario(
    usuario_id: str,
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    """Listar avaliações de um usuário"""
    return await service.get_by_usuario(usuario_id, page, limit)


@router.get("/mural/{mural_id}/estatisticas", response_model=Dict[str, Any])
async def estatisticas_mural(
    mural_id: str, service: AvaliacaoService = Depends(get_avaliacao_service)
):
    """Estatísticas de avaliação de um mural"""
    return await service.get_media_por_mural(mural_id)


@router.get("/{avaliacao_id}", response_model=Avaliacao)
async def obter_avaliacao(
    avaliacao_id: str, service: AvaliacaoService = Depends(get_avaliacao_service)
):
    """Obter avaliação por ID"""
    avaliacao = await service.get_by_id(avaliacao_id)
    if not avaliacao:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return avaliacao


@router.put("/{avaliacao_id}", response_model=dict)
async def atualizar_avaliacao(
    avaliacao_id: str,
    avaliacao_data: AvaliacaoUpdate,
    service: AvaliacaoService = Depends(get_avaliacao_service),
):
    """Atualizar avaliação"""
    success = await service.update_avaliacao(avaliacao_id, avaliacao_data)
    if not success:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return {"message": "Avaliação atualizada com sucesso"}


@router.delete("/{avaliacao_id}", response_model=dict)
async def deletar_avaliacao(
    avaliacao_id: str, service: AvaliacaoService = Depends(get_avaliacao_service)
):
    """Deletar avaliação"""
    success = await service.delete(avaliacao_id)
    if not success:
        raise HTTPException(status_code=404, detail="Avaliação não encontrada")
    return {"message": "Avaliação deletada com sucesso"}
