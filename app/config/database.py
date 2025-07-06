from config.settings import settings
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase


class DatabaseManager:
    client: AsyncIOMotorClient = None
    database: AsyncIOMotorDatabase = None


database_manager = DatabaseManager()


async def get_database() -> AsyncIOMotorDatabase:
    return database_manager.database


async def connect_to_mongo():
    """Conecta ao MongoDB"""
    database_manager.client = AsyncIOMotorClient(settings.MONGODB_URL)
    database_manager.database = database_manager.client[settings.DATABASE_NAME]

    await create_indexes()


async def close_mongo_connection():
    """Fecha a conexão com o MongoDB"""
    if database_manager.client:
        database_manager.client.close()


async def create_indexes():
    """Cria índices para otimizar consultas"""
    if database_manager.database is None:
        return

    await database_manager.database.murais.create_index("tags")
    await database_manager.database.murais.create_index("local.bairro")
    await database_manager.database.murais.create_index("artista_ids")
    await database_manager.database.murais.create_index("data_criacao")

    await database_manager.database.avaliacoes.create_index("mural_id")
    await database_manager.database.avaliacoes.create_index("usuario_id")
    await database_manager.database.avaliacoes.create_index(
        [("mural_id", 1), ("usuario_id", 1)], unique=True
    )

    await database_manager.database.usuarios.create_index("email", unique=True)

    await database_manager.database.artistas.create_index("nome")
