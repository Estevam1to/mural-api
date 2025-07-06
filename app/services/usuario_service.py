from datetime import datetime

from models.usuario import Usuario, UsuarioCreate, UsuarioUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase

from .base import BaseService


class UsuarioService(BaseService):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "usuarios")

    async def create_usuario(self, usuario_data: UsuarioCreate) -> str:
        """Cria um novo usuário"""
        existing = await self.collection.find_one({"email": usuario_data.email})
        if existing:
            raise ValueError("Email já cadastrado")

        data = usuario_data.dict(exclude={"senha"})
        data["senha_hash"] = Usuario.hash_password(usuario_data.senha)
        data["data_cadastro"] = datetime.utcnow()

        return await self.create(data)

    async def get_by_email(self, email: str):
        """Busca usuário por email"""
        document = await self.collection.find_one({"email": email})
        if document:
            document["_id"] = str(document["_id"])
        return document

    async def update_usuario(self, id: str, usuario_data: UsuarioUpdate) -> bool:
        """Atualiza um usuário"""
        data = usuario_data.dict(exclude_unset=True)

        if "email" in data:
            existing = await self.collection.find_one(
                {"email": data["email"], "_id": {"$ne": id}}
            )
            if existing:
                raise ValueError("Email já cadastrado")

        return await self.update(id, data)
