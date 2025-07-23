from datetime import datetime
from typing import Any, Dict, List, Optional

from models.mural import MuralCreate, MuralUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from .base import BaseService
from .artista_service import ArtistaService


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
            filters["artista_ids"] = {"$in": [ObjectId(artista_id)]}

        # Get paginated results
        skip = (page - 1) * limit
        murais = (
            await self.collection.find(filters).skip(skip).limit(limit).to_list(limit)
        )
        total = await self.collection.count_documents(filters)

        # Serialize each mural
        serialized_murais = [self._serialize_mural(mural) for mural in murais]

        return {
            "murais": serialized_murais,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
        }

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

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, limit: int = 10
    ):
        """Buscar murais por intervalo de datas"""
        filter_query = {"data_criacao": {"$gte": start_date, "$lte": end_date}}

        skip = (page - 1) * limit
        murais = (
            await self.collection.find(filter_query)
            .skip(skip)
            .limit(limit)
            .to_list(limit)
        )
        total = await self.collection.count_documents(filter_query)

        return {
            "murais": [self._serialize_mural(mural) for mural in murais],
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit,
        }

    async def get_by_year(self, year: int, page: int = 1, limit: int = 10):
        """Buscar murais por ano"""
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        return await self.get_by_date_range(start_date, end_date, page, limit)

    async def create(self, mural_data: dict) -> dict:
        """Criar mural com validação de relacionamentos"""
        # Converter HttpUrl para string se presente
        if "imagem_url" in mural_data and mural_data["imagem_url"]:
            mural_data["imagem_url"] = str(mural_data["imagem_url"])

        # Validar se artistas existem
        if "artista_ids" in mural_data and mural_data["artista_ids"]:
            artista_service = ArtistaService(self.database)
            for artista_id in mural_data["artista_ids"]:
                artista = await artista_service.get_by_id(artista_id)
                if not artista:
                    raise ValueError(f"Artista com ID {artista_id} não encontrado")

        # Converter string IDs para ObjectId
        if "artista_ids" in mural_data:
            mural_data["artista_ids"] = [
                ObjectId(id) for id in mural_data["artista_ids"]
            ]

        mural_data["data_criacao"] = datetime.utcnow()
        result = await self.collection.insert_one(mural_data)

        created_mural = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize_mural(created_mural)

    async def update(self, mural_id: str, update_data: dict) -> dict:
        """Atualizar mural com validação de relacionamentos"""
        # Converter HttpUrl para string se presente
        if "imagem_url" in update_data and update_data["imagem_url"]:
            update_data["imagem_url"] = str(update_data["imagem_url"])

        # Validar se artistas existem ao atualizar
        if "artista_ids" in update_data and update_data["artista_ids"]:
            artista_service = ArtistaService(self.database)
            for artista_id in update_data["artista_ids"]:
                artista = await artista_service.get_by_id(artista_id)
                if not artista:
                    raise ValueError(f"Artista com ID {artista_id} não encontrado")

            # Converter para ObjectId
            update_data["artista_ids"] = [
                ObjectId(id) for id in update_data["artista_ids"]
            ]

        # Remove campos None
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            raise ValueError("Nenhum campo válido para atualização")

        result = await self.collection.update_one(
            {"_id": ObjectId(mural_id)}, {"$set": update_data}
        )

        if result.matched_count == 0:
            return None

        updated_mural = await self.collection.find_one({"_id": ObjectId(mural_id)})
        return self._serialize_mural(updated_mural)

    def _serialize_mural(self, mural: dict) -> dict:
        """Serializa um mural para o formato de resposta"""
        if not mural:
            return None

        mural["id"] = str(mural["_id"])
        del mural["_id"]

        # Converter ObjectIds para strings
        if "artista_ids" in mural and mural["artista_ids"]:
            mural["artista_ids"] = [str(id) for id in mural["artista_ids"]]

        return mural
