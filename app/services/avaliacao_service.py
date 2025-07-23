from datetime import datetime
from typing import Any, Dict

from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from models.avaliacao import AvaliacaoCreate, AvaliacaoUpdate
from .base import BaseService
from .mural_service import MuralService
from .usuario_service import UsuarioService


class AvaliacaoService(BaseService):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "avaliacoes")

    async def create_avaliacao(
        self, avaliacao_data: AvaliacaoCreate
    ) -> dict:  # Changed return type
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

        # Verificar se mural existe
        mural_service = MuralService(self.database)
        mural = await mural_service.get_by_id(avaliacao_data.mural_id)
        if not mural:
            raise ValueError("Mural não encontrado")

        # Verificar se usuário existe
        usuario_service = UsuarioService(self.database)
        usuario = await usuario_service.get_by_id(avaliacao_data.usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado")

        data = avaliacao_data.dict()
        return await self.create(data)  # This returns the serialized dict

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

    async def create(self, avaliacao_data: dict) -> dict:
        """Criar avaliação com serialização"""
        avaliacao_data["data"] = datetime.utcnow()
        result = await self.collection.insert_one(avaliacao_data)

        created_avaliacao = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize_avaliacao(created_avaliacao)

    def _serialize_avaliacao(self, avaliacao: dict) -> dict:
        """Serializa uma avaliação para o formato de resposta"""
        if not avaliacao:
            return None

        avaliacao["id"] = str(avaliacao["_id"])
        del avaliacao["_id"]

        return avaliacao
