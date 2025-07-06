from typing import Optional

from pydantic import BaseModel, Field, validator


class LocalBase(BaseModel):
    nome: str = Field(..., min_length=1, max_length=200)
    latitude: float = Field(..., ge=-90, le=90)
    longitude: float = Field(..., ge=-180, le=180)
    bairro: str = Field(..., min_length=1, max_length=100)
    cidade: str = Field(..., min_length=1, max_length=100)

    @validator("latitude")
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError("Latitude deve estar entre -90 e 90")
        return v

    @validator("longitude")
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError("Longitude deve estar entre -180 e 180")
        return v


class LocalCreate(LocalBase):
    pass


class LocalUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=1, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    bairro: Optional[str] = Field(None, min_length=1, max_length=100)
    cidade: Optional[str] = Field(None, min_length=1, max_length=100)


class Local(LocalBase):
    id: str = Field(alias="_id")

    class Config:
        allow_population_by_field_name = True
        populate_by_name = True
