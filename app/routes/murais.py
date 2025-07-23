from typing import Any, Dict, List, Optional
from datetime import datetime
from fastapi import Query

from config.database import get_database
from fastapi import APIRouter, Depends, HTTPException, Query, Path
from models.mural import Mural, MuralCreate, MuralUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.mural_service import MuralService

router = APIRouter(prefix="/murais", tags=["murais"])


async def get_mural_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> MuralService:
    return MuralService(db)


@router.post("/", response_model=dict)
async def create_mural(
    mural: MuralCreate, db: AsyncIOMotorDatabase = Depends(get_database)
):
    """Criar um novo mural"""
    try:
        service = MuralService(db)
        result = await service.create(mural.dict())
        return result  # Return directly, not wrapped
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


@router.get("/top-artistas")
async def obter_top_artistas(
    limit: int = Query(5, ge=1, le=20, description="Número de artistas"),
    service: MuralService = Depends(get_mural_service),
):
    """F5 - Top artistas com mais murais"""
    return await service.get_top_artistas_by_murais(limit=limit)


@router.get("/media-por-bairro")
async def obter_media_avaliacao_por_bairro(
    service: MuralService = Depends(get_mural_service),
):
    """F6 - Média de avaliação por bairro"""
    return await service.get_media_avaliacao_por_bairro()


# MOVER ESTAS ROTAS PARA ANTES DA ROTA /{mural_id}
@router.get("/by-date-range")
async def obter_murais_por_periodo(
    start_date: str = Query(..., description="Data de início (YYYY-MM-DD)"),
    end_date: str = Query(..., description="Data de fim (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: MuralService = Depends(get_mural_service),
):
    """F7 - Filtrar murais por intervalo de datas"""
    try:
        # Converter strings para datetime
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = datetime.strptime(end_date + " 23:59:59", "%Y-%m-%d %H:%M:%S")

        return await service.get_by_date_range(
            start_datetime, end_datetime, page, limit
        )
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=f"Formato de data inválido. Use YYYY-MM-DD. Erro: {str(e)}",
        )
    except Exception as e:
        print(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


@router.get("/by-year/{year}")
async def obter_murais_por_ano(
    year: int = Path(..., description="Ano (ex: 2025)"),
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: MuralService = Depends(get_mural_service),
):
    """F8 - Filtrar murais por ano"""
    try:
        return await service.get_by_year(year, page, limit)
    except Exception as e:
        print(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


# ESTA ROTA DEVE VIR POR ÚLTIMO (depois das rotas específicas)
@router.get("/{mural_id}", response_model=dict)
async def obter_mural(
    mural_id: str, service: MuralService = Depends(get_mural_service)
):
    """F3 - Obter mural por ID"""
    try:
        mural = await service.get_by_id(mural_id)
        if not mural:
            raise HTTPException(status_code=404, detail="Mural não encontrado")
        return mural
    except ValueError:
        raise HTTPException(status_code=400, detail="ID do mural inválido")
    except Exception as e:
        print(f"Erro interno: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")


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
