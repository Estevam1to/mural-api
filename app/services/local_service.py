from motor.motor_asyncio import AsyncIOMotorDatabase

from models.local import LocalCreate, LocalUpdate
from .base import BaseService


class LocalService(BaseService):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "locais")

    async def create_local(self, local_data: LocalCreate) -> str:
        """Cria um novo local"""
        data = local_data.dict()
        return await self.create(data)

    async def update_local(self, id: str, local_data: LocalUpdate) -> bool:
        """Atualiza um local"""
        data = local_data.dict(exclude_unset=True)
        return await self.update(id, data)

    async def search_by_city(self, cidade: str):
        """Busca locais por cidade"""
        filters = {"cidade": {"$regex": cidade, "$options": "i"}}
        cursor = self.collection.find(filters)
        documents = await cursor.to_list(length=100)

        for doc in documents:
            doc["_id"] = str(doc["_id"])

        return documents

    async def search_by_neighborhood(self, bairro: str):
        """Busca locais por bairro"""
        filters = {"bairro": {"$regex": bairro, "$options": "i"}}
        cursor = self.collection.find(filters)
        documents = await cursor.to_list(length=100)

        for doc in documents:
            doc["_id"] = str(doc["_id"])

        return documents
