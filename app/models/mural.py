from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, validator


class MuralBase(BaseModel):
    titulo: str = Field(..., min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    imagem_url: Optional[HttpUrl] = None
    tags: List[str] = Field(default_factory=list)


class MuralCreate(MuralBase):
    local_id: str = Field(..., description="ID do local onde está o mural")
    artista_ids: List[str] = Field(default_factory=list)


class MuralUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=1, max_length=200)
    descricao: Optional[str] = Field(None, max_length=2000)
    imagem_url: Optional[HttpUrl] = None
    tags: Optional[List[str]] = None
    local_id: Optional[str] = None
    artista_ids: Optional[List[str]] = None


class Mural(MuralBase):
    id: str = Field(alias="_id")
    data_criacao: datetime
    local_id: str
    artista_ids: List[str] = Field(default_factory=list)

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
