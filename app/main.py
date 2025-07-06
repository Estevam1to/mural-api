from contextlib import asynccontextmanager

import uvicorn
from config.database import close_mongo_connection, connect_to_mongo
from config.settings import Settings
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import artistas, avaliacoes, locais, murais, usuarios

settings = Settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()


app = FastAPI(
    title="Mural Map API",
    description="API para gerenciar murais, artistas e avaliações de arte urbana.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(murais.router)
app.include_router(artistas.router)
app.include_router(usuarios.router)
app.include_router(avaliacoes.router)
app.include_router(locais.router)


@app.get("/")
async def root():
    return {
        "message": "Mural Map API",
        "version": settings.api_version,
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
