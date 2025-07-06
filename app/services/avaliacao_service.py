from datetime import datetime
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase

from models.avaliacao import AvaliacaoCreate, AvaliacaoUpdate
from .base import BaseService


class AvaliacaoService(BaseService):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "avaliacoes")

    async def create_avaliacao(self, avaliacao_data: AvaliacaoCreate) -> str:
        """Cria uma nova avaliação"""
        # Verificar se usuário já avaliou este mural
        existing = await self.collection.find_one(
            {
                "mural_id": avaliacao_data.mural_id,
                "usuario_id": avaliacao_data.usuario_id,
            }
        )
        if existing:
            raise ValueError("Usuário já avaliou este mural")

        data = avaliacao_data.dict()
        data["data"] = datetime.utcnow()
        return await self.create(data)

    async def update_avaliacao(self, id: str, avaliacao_data: AvaliacaoUpdate) -> bool:
        """Atualiza uma avaliação"""
        data = avaliacao_data.dict(exclude_unset=True)
        return await self.update(id, data)

    async def get_by_mural(self, mural_id: str, page: int = 1, limit: int = 10):
        """Lista avaliações de um mural"""
        filters = {"mural_id": mural_id}
        return await self.list_with_pagination(
            filters=filters, page=page, limit=limit, sort_by="data", sort_order=-1
        )

    async def get_by_usuario(self, usuario_id: str, page: int = 1, limit: int = 10):
        """Lista avaliações de um usuário"""
        filters = {"usuario_id": usuario_id}
        return await self.list_with_pagination(
            filters=filters, page=page, limit=limit, sort_by="data", sort_order=-1
        )

    async def get_media_por_mural(self, mural_id: str) -> Dict[str, Any]:
        """Calcula média de avaliação de um mural"""
        pipeline = [
            {"$match": {"mural_id": mural_id}},
            {
                "$group": {
                    "_id": None,
                    "media": {"$avg": "$nota"},
                    "total": {"$sum": 1},
                    "distribuicao": {"$push": "$nota"},
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=1)

        if not result:
            return {"media": 0, "total": 0, "distribuicao": {}}

        data = result[0]

        # Calcular distribuição de notas
        distribuicao = {}
        for nota in data.get("distribuicao", []):
            distribuicao[str(nota)] = distribuicao.get(str(nota), 0) + 1

        return {
            "media": round(data.get("media", 0), 2),
            "total": data.get("total", 0),
            "distribuicao": distribuicao,
        }
