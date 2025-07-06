from motor.motor_asyncio import AsyncIOMotorDatabase

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
