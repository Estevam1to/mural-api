from typing import Any, Dict, Optional

from bson import ObjectId
from bson.errors import InvalidId
from motor.motor_asyncio import AsyncIOMotorDatabase


class BaseService:
    def __init__(self, database: AsyncIOMotorDatabase, collection_name: str):
        self.database = database
        self.collection = database[collection_name]

    async def create(self, data: dict) -> str:
        """Cria um novo documento"""
        result = await self.collection.insert_one(data)
        return str(result.inserted_id)

    async def get_by_id(self, id: str) -> Optional[dict]:
        """Busca um documento por ID"""
        try:
            object_id = ObjectId(id)
        except InvalidId:
            return None

        document = await self.collection.find_one({"_id": object_id})
        if document:
            document["_id"] = str(document["_id"])
        return document

    async def update(self, id: str, data: dict) -> bool:
        """Atualiza um documento"""
        try:
            object_id = ObjectId(id)
        except InvalidId:
            return False

        # Remove campos None/vazios
        update_data = {k: v for k, v in data.items() if v is not None}
        if not update_data:
            return False

        result = await self.collection.update_one(
            {"_id": object_id}, {"$set": update_data}
        )
        return result.modified_count > 0

    async def delete(self, id: str) -> bool:
        """Deleta um documento"""
        try:
            object_id = ObjectId(id)
        except InvalidId:
            return False

        result = await self.collection.delete_one({"_id": object_id})
        return result.deleted_count > 0

    async def list_with_pagination(
        self,
        filters: dict = None,
        page: int = 1,
        limit: int = 10,
        sort_by: str = "_id",
        sort_order: int = 1,
    ) -> Dict[str, Any]:
        """Lista documentos com paginação"""
        if filters is None:
            filters = {}

        skip = (page - 1) * limit

        # Contar total de documentos
        total = await self.collection.count_documents(filters)

        # Buscar documentos
        cursor = (
            self.collection.find(filters)
            .sort(sort_by, sort_order)
            .skip(skip)
            .limit(limit)
        )
        documents = await cursor.to_list(length=limit)

        # Converter ObjectId para string
        for doc in documents:
            doc["_id"] = str(doc["_id"])

        return {
            "items": documents,
            "total": total,
            "page": page,
            "limit": limit,
            "pages": (total + limit - 1) // limit,
        }

    async def count(self, filters: dict = None) -> int:
        """Conta documentos com filtros"""
        if filters is None:
            filters = {}
        return await self.collection.count_documents(filters)
