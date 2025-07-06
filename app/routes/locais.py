from typing import List

from config.database import get_database
from fastapi import APIRouter, Depends, HTTPException, Query
from models.local import Local, LocalCreate, LocalUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.local_service import LocalService

router = APIRouter(prefix="/locais", tags=["locais"])


async def get_local_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> LocalService:
    return LocalService(db)


@router.post("/", response_model=dict, status_code=201)
async def criar_local(
    local: LocalCreate, service: LocalService = Depends(get_local_service)
):
    """Criar novo local"""
    try:
        local_id = await service.create_local(local)
        return {"id": local_id, "message": "Local criado com sucesso"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/", response_model=dict)
async def listar_locais(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: LocalService = Depends(get_local_service),
):
    """Listar locais com paginação"""
    return await service.list_with_pagination(page=page, limit=limit)


@router.get("/search/cidade", response_model=List[Local])
async def buscar_locais_por_cidade(
    cidade: str = Query(..., description="Nome da cidade"),
    service: LocalService = Depends(get_local_service),
):
    """Buscar locais por cidade"""
    return await service.search_by_city(cidade)


@router.get("/search/bairro", response_model=List[Local])
async def buscar_locais_por_bairro(
    bairro: str = Query(..., description="Nome do bairro"),
    service: LocalService = Depends(get_local_service),
):
    """Buscar locais por bairro"""
    return await service.search_by_neighborhood(bairro)


@router.get("/{local_id}", response_model=Local)
async def obter_local(
    local_id: str, service: LocalService = Depends(get_local_service)
):
    """Obter local por ID"""
    local = await service.get_by_id(local_id)
    if not local:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return local


@router.put("/{local_id}", response_model=dict)
async def atualizar_local(
    local_id: str,
    local_data: LocalUpdate,
    service: LocalService = Depends(get_local_service),
):
    """Atualizar local"""
    success = await service.update_local(local_id, local_data)
    if not success:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return {"message": "Local atualizado com sucesso"}


@router.delete("/{local_id}", response_model=dict)
async def deletar_local(
    local_id: str, service: LocalService = Depends(get_local_service)
):
    """Deletar local"""
    success = await service.delete(local_id)
    if not success:
        raise HTTPException(status_code=404, detail="Local não encontrado")
    return {"message": "Local deletado com sucesso"}
