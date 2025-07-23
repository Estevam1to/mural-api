from datetime import datetime
from typing import Any, Dict, List, Optional

from models.mural import MuralCreate, MuralUpdate
from models.local import LocalCreate
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from .base import BaseService
from .artista_service import ArtistaService
from .local_service import LocalService


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
        # Construir pipeline de agregação para fazer lookup com locais
        pipeline = []

        # Fazer lookup com a coleção de locais
        pipeline.append(
            {
                "$lookup": {
                    "from": "locais",
                    "localField": "local_id",
                    "foreignField": "_id",
                    "as": "local",
                }
            }
        )

        # Unwind para transformar array em objeto
        pipeline.append(
            {"$unwind": {"path": "$local", "preserveNullAndEmptyArrays": True}}
        )

        # Aplicar filtros
        match_filters = {}

        if bairro:
            match_filters["local.bairro"] = {"$regex": bairro, "$options": "i"}

        if tag:
            match_filters["tags"] = {"$in": [tag]}

        if artista_id:
            match_filters["artista_ids"] = {"$in": [ObjectId(artista_id)]}

        if match_filters:
            pipeline.append({"$match": match_filters})

        # Adicionar paginação
        pipeline.extend([{"$skip": (page - 1) * limit}, {"$limit": limit}])

        # Executar agregação
        murais = await self.collection.aggregate(pipeline).to_list(limit)

        # Contar total (sem paginação)
        count_pipeline = [
            {
                "$lookup": {
                    "from": "locais",
                    "localField": "local_id",
                    "foreignField": "_id",
                    "as": "local",
                }
            },
            {"$unwind": {"path": "$local", "preserveNullAndEmptyArrays": True}},
        ]

        if match_filters:
            count_pipeline.append({"$match": match_filters})

        count_pipeline.append({"$count": "total"})

        total_result = await self.collection.aggregate(count_pipeline).to_list(1)
        total = total_result[0]["total"] if total_result else 0

        # Serialize each mural
        serialized_murais = [
            self._serialize_mural_with_local(mural) for mural in murais
        ]

        return {
            "murais": serialized_murais,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
        }

    async def count_by_bairro(self, bairro: str) -> int:
        """Conta murais por bairro"""
        pipeline = [
            {
                "$lookup": {
                    "from": "locais",
                    "localField": "local_id",
                    "foreignField": "_id",
                    "as": "local",
                }
            },
            {"$unwind": {"path": "$local", "preserveNullAndEmptyArrays": True}},
            {"$match": {"local.bairro": {"$regex": bairro, "$options": "i"}}},
            {"$count": "total"},
        ]

        result = await self.collection.aggregate(pipeline).to_list(1)
        return result[0]["total"] if result else 0

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
                    "artista_id": {
                        "$toString": "$_id"
                    },  # Converter ObjectId para string
                    "nome": "$artista.nome",
                    "biografia": "$artista.biografia",
                    "total_murais": 1,
                    "_id": 0,  # Remover o campo _id do resultado
                }
            },
        ]

        cursor = self.collection.aggregate(pipeline)
        result = await cursor.to_list(length=limit)

        # Garantir que todos os ObjectIds sejam serializados
        for item in result:
            if "artista_id" in item and isinstance(item["artista_id"], ObjectId):
                item["artista_id"] = str(item["artista_id"])

        return result

    async def get_media_avaliacao_por_bairro(self) -> List[Dict[str, Any]]:
        """Retorna média de avaliação por bairro"""
        pipeline = [
            {
                "$lookup": {
                    "from": "locais",
                    "localField": "local_id",
                    "foreignField": "_id",
                    "as": "local",
                }
            },
            {"$unwind": {"path": "$local", "preserveNullAndEmptyArrays": True}},
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
            {
                "$project": {
                    "bairro": "$_id",
                    "media_avaliacao": {"$round": ["$media_avaliacao", 2]},
                    "total_avaliacoes": 1,
                    "_id": 0,  # Remover o campo _id
                }
            },
            {"$sort": {"media_avaliacao": -1}},
        ]

        cursor = self.collection.aggregate(pipeline)
        return await cursor.to_list(length=None)

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """Filtrar murais por intervalo de datas"""
        # Construir pipeline de agregação
        pipeline = []

        # Fazer lookup com a coleção de locais
        pipeline.append(
            {
                "$lookup": {
                    "from": "locais",
                    "localField": "local_id",
                    "foreignField": "_id",
                    "as": "local",
                }
            }
        )

        # Unwind para transformar array em objeto
        pipeline.append(
            {"$unwind": {"path": "$local", "preserveNullAndEmptyArrays": True}}
        )

        # Filtro por data
        pipeline.append(
            {
                "$match": {
                    "data_criacao": {
                        "$gte": start_date,
                        "$lte": end_date,
                    }
                }
            }
        )

        # Adicionar paginação
        pipeline.extend([{"$skip": (page - 1) * limit}, {"$limit": limit}])

        # Executar agregação
        murais = await self.collection.aggregate(pipeline).to_list(limit)

        # Contar total (sem paginação)
        count_pipeline = [
            {
                "$lookup": {
                    "from": "locais",
                    "localField": "local_id",
                    "foreignField": "_id",
                    "as": "local",
                }
            },
            {"$unwind": {"path": "$local", "preserveNullAndEmptyArrays": True}},
            {
                "$match": {
                    "data_criacao": {
                        "$gte": start_date,
                        "$lte": end_date,
                    }
                }
            },
            {"$count": "total"},
        ]

        total_result = await self.collection.aggregate(count_pipeline).to_list(1)
        total = total_result[0]["total"] if total_result else 0

        # Serialize each mural
        serialized_murais = [
            self._serialize_mural_with_local(mural) for mural in murais
        ]

        return {
            "murais": serialized_murais,
            "total": total,
            "page": page,
            "pages": (total + limit - 1) // limit if total > 0 else 0,
            "periodo": {
                "inicio": start_date.isoformat(),
                "fim": end_date.isoformat(),
            },
        }

    async def get_by_year(
        self, year: int, page: int = 1, limit: int = 10
    ) -> Dict[str, Any]:
        """Filtrar murais por ano"""
        # Criar datas de início e fim do ano
        start_date = datetime(year, 1, 1)
        end_date = datetime(year, 12, 31, 23, 59, 59)

        return await self.get_by_date_range(start_date, end_date, page, limit)

    def _validar_local(self, local_data: dict) -> dict:
        """Valida os dados do local"""
        campos_obrigatorios = ["nome", "latitude", "longitude", "bairro", "cidade"]

        for campo in campos_obrigatorios:
            if campo not in local_data:
                raise ValueError(f"Campo '{campo}' é obrigatório no local")

        # Validar tipos e valores
        if not isinstance(local_data["latitude"], (int, float)) or not (
            -90 <= local_data["latitude"] <= 90
        ):
            raise ValueError("Latitude deve ser um número entre -90 e 90")

        if not isinstance(local_data["longitude"], (int, float)) or not (
            -180 <= local_data["longitude"] <= 180
        ):
            raise ValueError("Longitude deve ser um número entre -180 e 180")

        if not local_data["nome"].strip():
            raise ValueError("Nome do local não pode ser vazio")

        if len(local_data["nome"]) > 200:
            raise ValueError("Nome do local deve ter no máximo 200 caracteres")

        return local_data

    async def create(self, mural_data: dict) -> dict:
        """Criar mural com validação de relacionamentos"""
        # Converter HttpUrl para string se presente
        if "imagem_url" in mural_data and mural_data["imagem_url"]:
            mural_data["imagem_url"] = str(mural_data["imagem_url"])

        # Validar se local existe
        if "local_id" in mural_data and mural_data["local_id"]:
            local_service = LocalService(self.database)
            local = await local_service.get_by_id(mural_data["local_id"])
            if not local:
                raise ValueError(
                    f"Local com ID {mural_data['local_id']} não encontrado"
                )

            # Converter para ObjectId
            mural_data["local_id"] = ObjectId(mural_data["local_id"])

        # Validar se artistas existem
        if "artista_ids" in mural_data and mural_data["artista_ids"]:
            artista_service = ArtistaService(self.database)
            for artista_id in mural_data["artista_ids"]:
                artista = await artista_service.get_by_id(artista_id)
                if not artista:
                    raise ValueError(f"Artista com ID {artista_id} não encontrado")

            # Converter string IDs para ObjectId
            mural_data["artista_ids"] = [
                ObjectId(id) for id in mural_data["artista_ids"]
            ]

        mural_data["data_criacao"] = datetime.utcnow()
        result = await self.collection.insert_one(mural_data)

        created_mural = await self.collection.find_one({"_id": result.inserted_id})
        return self._serialize_mural(created_mural)

    def _serialize_mural(self, mural: dict) -> dict:
        """Serializa um mural para o formato de resposta"""
        if not mural:
            return None

        mural["id"] = str(mural["_id"])
        del mural["_id"]

        # Converter ObjectIds para strings
        if "local_id" in mural and mural["local_id"]:
            mural["local_id"] = str(mural["local_id"])

        if "artista_ids" in mural and mural["artista_ids"]:
            mural["artista_ids"] = [str(id) for id in mural["artista_ids"]]

        return mural

    def _serialize_mural_with_local(self, mural: dict) -> dict:
        """Serializa um mural com dados do local incluídos"""
        if not mural:
            return None

        # Converter _id principal para string
        mural["id"] = str(mural["_id"])
        del mural["_id"]

        # Converter ObjectIds para strings
        if "local_id" in mural and mural["local_id"]:
            mural["local_id"] = str(mural["local_id"])

        if "artista_ids" in mural and mural["artista_ids"]:
            mural["artista_ids"] = [str(id) for id in mural["artista_ids"]]

        # Serializar dados do local se existir
        if "local" in mural and mural["local"]:
            local = mural["local"]
            if "_id" in local:
                local["id"] = str(local["_id"])
                del local["_id"]

        return mural

    async def get_by_id(self, mural_id: str) -> dict:
        """Obter mural por ID com dados do local"""
        try:
            # Pipeline para fazer lookup com local
            pipeline = [
                {"$match": {"_id": ObjectId(mural_id)}},
                {
                    "$lookup": {
                        "from": "locais",
                        "localField": "local_id",
                        "foreignField": "_id",
                        "as": "local",
                    }
                },
                {"$unwind": {"path": "$local", "preserveNullAndEmptyArrays": True}},
            ]

            result = await self.collection.aggregate(pipeline).to_list(1)

            if not result:
                return None

            mural = result[0]
            return self._serialize_mural_with_local(mural)

        except Exception as e:
            print(f"Erro ao buscar mural {mural_id}: {e}")
            return None
