from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId
from datetime import datetime

from models.artista import ArtistaCreate, ArtistaUpdate
from .base import BaseService


class ArtistaService(BaseService):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "artistas")

    async def create_artista(self, artista_data: ArtistaCreate) -> str:
        """Cria um novo artista"""
        data = artista_data.dict()
        return await self.create(data)

    async def update_artista(self, id: str, artista_data: ArtistaUpdate) -> bool:
        """Atualiza um artista"""
        data = artista_data.dict(exclude_unset=True)
        return await self.update(id, data)

    async def search_by_name(self, name: str):
        """Busca artistas por nome"""
        filters = {"nome": {"$regex": name, "$options": "i"}}
        cursor = self.collection.find(filters)
        documents = await cursor.to_list(length=100)

        for doc in documents:
            doc["_id"] = str(doc["_id"])

        return documents

    async def create(self, artista_data: dict) -> dict:
        """Criar artista com conversão de tipos"""
        # Converter HttpUrl para string se presente
        if "site" in artista_data and artista_data["site"]:
            artista_data["site"] = str(artista_data["site"])

        # Adicionar data de criação
        artista_data["data_criacao"] = datetime.utcnow()

        result = await self.collection.insert_one(artista_data)
        created_artista = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize_artista(created_artista)

    async def update(self, artista_id: str, update_data: dict) -> dict:
        """Atualizar artista com conversão de tipos"""
        # Converter HttpUrl para string se presente
        if "site" in update_data and update_data["site"]:
            update_data["site"] = str(update_data["site"])

        # Remove campos None
        update_data = {k: v for k, v in update_data.items() if v is not None}

        if not update_data:
            raise ValueError("Nenhum campo válido para atualização")

        result = await self.collection.update_one(
            {"_id": ObjectId(artista_id)}, {"$set": update_data}
        )

        if result.matched_count == 0:
            return None

        updated_artista = await self.collection.find_one({"_id": ObjectId(artista_id)})
        return self._serialize_artista(updated_artista)

    def _serialize_artista(self, artista: dict) -> dict:
        """Serializa um artista para o formato de resposta"""
        if not artista:
            return None

        artista["id"] = str(artista["_id"])
        del artista["_id"]

        return artista
