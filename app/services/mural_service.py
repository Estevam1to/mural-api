from datetime import datetime
from typing import Any, Dict, List, Optional

from models.mural import MuralCreate, MuralUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base import BaseService


class MuralService(BaseService):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "murais")

    async def create_mural(self, mural_data: MuralCreate) -> str:
        """Cria um novo mural"""
        data = mural_data.dict()
        data["data_criacao"] = datetime.utcnow()
        return await self.create(data)

    async def list_murais(
        self,
        bairro: Optional[str] = None,
        tag: Optional[str] = None,
        artista_id: Optional[str] = None,
        page: int = 1,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Lista murais com filtros"""
        filters = {}

        if bairro:
            filters["local.bairro"] = {"$regex": bairro, "$options": "i"}

        if tag:
            filters["tags"] = {"$in": [tag]}

        if artista_id:
            filters["artista_ids"] = {"$in": [artista_id]}

        return await self.list_with_pagination(
            filters=filters,
            page=page,
            limit=limit,
            sort_by="data_criacao",
            sort_order=-1,
        )

    async def count_by_bairro(self, bairro: str) -> int:
        """Conta murais por bairro"""
        filters = {"local.bairro": {"$regex": bairro, "$options": "i"}}
        return await self.count(filters)

    async def update_mural(self, id: str, mural_data: MuralUpdate) -> bool:
        """Atualiza um mural"""
        data = mural_data.dict(exclude_unset=True)
        return await self.update(id, data)

    async def get_top_artistas_by_murais(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Retorna top artistas com mais murais"""
        pipeline = [
            {"$unwind": "$artista_ids"},
            {"$group": {"_id": "$artista_ids", "total_murais": {"$sum": 1}}},
            {"$sort": {"total_murais": -1}},
            {"$limit": limit},
            {
                "$lookup": {
                    "from": "artistas",
                    "localField": "_id",
                    "foreignField": "_id",
                    "as": "artista",
                }
            },
            {"$unwind": "$artista"},
            {
                "$project": {
                    "artista_id": "$_id",
                    "nome": "$artista.nome",
                    "total_murais": 1,
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=limit)

    async def get_media_avaliacao_por_bairro(self) -> List[Dict[str, Any]]:
        """Retorna média de avaliação por bairro"""
        pipeline = [
            {
                "$lookup": {
                    "from": "avaliacoes",
                    "localField": "_id",
                    "foreignField": "mural_id",
                    "as": "avaliacoes",
                }
            },
            {"$unwind": {"path": "$avaliacoes", "preserveNullAndEmptyArrays": True}},
            {
                "$group": {
                    "_id": "$local.bairro",
                    "media_avaliacao": {"$avg": "$avaliacoes.nota"},
                    "total_avaliacoes": {"$sum": 1},
                }
            },
            {"$sort": {"media_avaliacao": -1}},
        ]

        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)
