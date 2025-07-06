from typing import Dict, Optional

from pydantic import BaseModel, Field, HttpUrl


class ArtistaBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    biografia: Optional[str] = Field(None, max_length=2000)
    site: Optional[HttpUrl] = None
    redes_sociais: Optional[Dict[str, str]] = Field(default_factory=dict)


class ArtistaCreate(ArtistaBase):
    pass


class ArtistaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    biografia: Optional[str] = Field(None, max_length=2000)
    site: Optional[HttpUrl] = None
    redes_sociais: Optional[Dict[str, str]] = None


class Artista(ArtistaBase):
    id: str = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
