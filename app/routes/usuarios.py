from config.database import get_database
from fastapi import APIRouter, Depends, HTTPException, Query
from models.usuario import Usuario, UsuarioCreate, UsuarioLogin, UsuarioUpdate
from motor.motor_asyncio import AsyncIOMotorDatabase
from services.usuario_service import UsuarioService

router = APIRouter(prefix="/usuarios", tags=["usuarios"])


async def get_usuario_service(
    db: AsyncIOMotorDatabase = Depends(get_database),
) -> UsuarioService:
    return UsuarioService(db)


@router.post("/", response_model=dict, status_code=201)
async def criar_usuario(
    usuario: UsuarioCreate, service: UsuarioService = Depends(get_usuario_service)
):
    """Criar novo usuário"""
    try:
        usuario_id = await service.create_usuario(usuario)
        return {"id": usuario_id, "message": "Usuário criado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/login", response_model=dict)
async def login_usuario(
    login_data: UsuarioLogin, service: UsuarioService = Depends(get_usuario_service)
):
    """Login de usuário"""
    usuario = await service.get_by_email(login_data.email)
    if not usuario:
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    usuario_obj = Usuario(**usuario)
    if not usuario_obj.verify_password(login_data.senha):
        raise HTTPException(status_code=401, detail="Email ou senha incorretos")

    return {"message": "Login realizado com sucesso", "user_id": usuario["_id"]}


@router.get("/", response_model=dict)
async def listar_usuarios(
    page: int = Query(1, ge=1, description="Número da página"),
    limit: int = Query(10, ge=1, le=100, description="Itens por página"),
    service: UsuarioService = Depends(get_usuario_service),
):
    """Listar usuários com paginação"""
    return await service.list_with_pagination(page=page, limit=limit)


@router.get("/{usuario_id}", response_model=Usuario)
async def obter_usuario(
    usuario_id: str, service: UsuarioService = Depends(get_usuario_service)
):
    """Obter usuário por ID"""
    usuario = await service.get_by_id(usuario_id)
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return usuario


@router.put("/{usuario_id}", response_model=dict)
async def atualizar_usuario(
    usuario_id: str,
    usuario_data: UsuarioUpdate,
    service: UsuarioService = Depends(get_usuario_service),
):
    """Atualizar usuário"""
    try:
        success = await service.update_usuario(usuario_id, usuario_data)
        if not success:
            raise HTTPException(status_code=404, detail="Usuário não encontrado")
        return {"message": "Usuário atualizado com sucesso"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{usuario_id}", response_model=dict)
async def deletar_usuario(
    usuario_id: str, service: UsuarioService = Depends(get_usuario_service)
):
    """Deletar usuário"""
    success = await service.delete(usuario_id)
    if not success:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return {"message": "Usuário deletado com sucesso"}
