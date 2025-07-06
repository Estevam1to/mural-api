from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, validator


class AvaliacaoBase(BaseModel):
    nota: int = Field(..., ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=1000)

    @validator("nota")
    def validate_nota(cls, v):
        if not 1 <= v <= 5:
            raise ValueError("Nota deve estar entre 1 e 5")
        return v


class AvaliacaoCreate(AvaliacaoBase):
    mural_id: str
    usuario_id: str


class AvaliacaoUpdate(BaseModel):
    nota: Optional[int] = Field(None, ge=1, le=5)
    comentario: Optional[str] = Field(None, max_length=1000)

    @validator("nota")
    def validate_nota(cls, v):
        if v is not None and not 1 <= v <= 5:
            raise ValueError("Nota deve estar entre 1 e 5")
        return v


class Avaliacao(AvaliacaoBase):
    id: str = Field(alias="_id")
    mural_id: str
    usuario_id: str
    data: datetime

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
