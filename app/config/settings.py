from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    MONGODB_URL: str = "mongodb://localhost:27017"
    DATABASE_NAME: str = "mural_map"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()