from datetime import datetime
from typing import Optional

from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    email: EmailStr


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, max_length=100)


class UsuarioLogin(BaseModel):
    email: EmailStr
    senha: str


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    email: Optional[EmailStr] = None


class Usuario(UsuarioBase):
    id: str = Field(alias="_id")
    senha_hash: str
    data_cadastro: datetime

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True

    @classmethod
    def hash_password(cls, password: str) -> str:
        return pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.senha_hash)
