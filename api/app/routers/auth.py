"""
Router para Autenticação e Gestão de Usuários (Login / Cadastro).
Integra com as tabelas 'usuarios', 'perfis' e 'pessoas' do PostgreSQL no Neon.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_access_token,
)
from app.models.db_models import Usuario, Perfil, Pessoa
from app.models.schemas import (
    UserRegisterRequest,
    UserLoginRequest,
    AuthResponse,
    UsuarioDTO,
)

router = APIRouter(prefix="/auth", tags=["Autenticação & Usuários"])


async def get_current_user(
    authorization: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    """Dependency para rotas que exigem usuário autenticado"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação não fornecido ou inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.split(" ")[1]
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão expirada ou token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    stmt = (
        select(Usuario)
        .options(selectinload(Usuario.pessoa), selectinload(Usuario.perfil))
        .where(Usuario.id == user_id, Usuario.ativo == True)
    )
    res = await db.execute(stmt)
    user = res.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado ou inativo",
        )

    return user


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    data: UserRegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Cadastra um novo usuário no sistema:
    1. Valida se o login já existe
    2. Cria ou vincula uma Pessoa correspondente
    3. Criptografa a senha com bcrypt
    4. Registra na tabela 'usuarios' e emite o token JWT
    """
    login_clean = data.login.strip().lower()

    # 1. Verifica duplicidade de login
    stmt = select(Usuario).where(Usuario.login == login_clean)
    res = await db.execute(stmt)
    if res.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este nome de usuário já está em uso. Por favor, escolha outro.",
        )

    # 2. Localiza ou cria a Pessoa correspondente
    pessoa: Optional[Pessoa] = None
    if data.cpf_cnpj:
        clean_doc = data.cpf_cnpj.strip()
        stmt_p = select(Pessoa).where(Pessoa.cpf_cnpj == clean_doc)
        res_p = await db.execute(stmt_p)
        pessoa = res_p.scalars().first()

    if not pessoa:
        pessoa = Pessoa(
            razao_social=data.nome.strip(),
            cpf_cnpj=data.cpf_cnpj.strip() if data.cpf_cnpj else None,
            tipo="FATURADO",
            ativo=True,
        )
        db.add(pessoa)
        await db.flush()

    # 3. Valida Perfil
    perfil = await db.get(Perfil, data.perfil_id)
    if not perfil:
        # Padrão: 2 (COMUM)
        perfil = await db.get(Perfil, 2)
        if not perfil:
            perfil = Perfil(id=2, nome="COMUM")
            db.add(perfil)
            await db.flush()

    # 4. Criação do Usuário com senha hash bcrypt
    novo_usuario = Usuario(
        login=login_clean,
        senha_hash=hash_password(data.senha),
        pessoa_id=pessoa.id,
        perfil_id=perfil.id,
        tentativas_falhas=0,
        ativo=True,
        ultimo_acesso=datetime.now(timezone.utc),
    )
    db.add(novo_usuario)
    await db.commit()

    # Carrega relacionamentos para o DTO
    stmt_load = (
        select(Usuario)
        .options(selectinload(Usuario.pessoa), selectinload(Usuario.perfil))
        .where(Usuario.id == novo_usuario.id)
    )
    res_load = await db.execute(stmt_load)
    usuario_completo = res_load.scalars().first()

    # 5. Gera JWT
    token = create_access_token(
        data={
            "sub": usuario_completo.login,
            "user_id": usuario_completo.id,
            "perfil": usuario_completo.perfil.nome if usuario_completo.perfil else "COMUM",
        }
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        usuario=UsuarioDTO(
            id=usuario_completo.id,
            login=usuario_completo.login,
            nome=usuario_completo.pessoa.razao_social if usuario_completo.pessoa else usuario_completo.login,
            perfil=usuario_completo.perfil.nome if usuario_completo.perfil else "COMUM",
            pessoa_id=usuario_completo.pessoa_id,
            ativo=usuario_completo.ativo,
            created_at=usuario_completo.created_at,
        ),
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    data: UserLoginRequest,
    db: AsyncSession = Depends(get_db),
) -> AuthResponse:
    """
    Autenticação de Usuário:
    - Validação de login e hash da senha
    - Controle de tentativas falhas e bloqueio temporário
    - Retorno do token JWT de sessão
    """
    login_clean = data.login.strip().lower()

    stmt = (
        select(Usuario)
        .options(selectinload(Usuario.pessoa), selectinload(Usuario.perfil))
        .where(Usuario.login == login_clean)
    )
    res = await db.execute(stmt)
    usuario = res.scalars().first()

    if not usuario or not usuario.ativo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos.",
        )

    # Verifica bloqueio por tentativas
    agora = datetime.now(timezone.utc)
    if usuario.bloqueado_ate and usuario.bloqueado_ate > agora:
        minutos_restantes = max(1, int((usuario.bloqueado_ate - agora).total_seconds() / 60))
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Conta temporariamente bloqueada por excesso de tentativas. Tente novamente em {minutos_restantes} minuto(s).",
        )

    # Validação da senha
    if not verify_password(data.senha, usuario.senha_hash):
        usuario.tentativas_falhas += 1
        if usuario.tentativas_falhas >= 5:
            usuario.bloqueado_ate = agora + timedelta(minutes=15)
        await db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos.",
        )

    # Login bem-sucedido: limpa falhas e atualiza último acesso
    usuario.tentativas_falhas = 0
    usuario.bloqueado_ate = None
    usuario.ultimo_acesso = agora
    await db.commit()

    token = create_access_token(
        data={
            "sub": usuario.login,
            "user_id": usuario.id,
            "perfil": usuario.perfil.nome if usuario.perfil else "COMUM",
        }
    )

    return AuthResponse(
        access_token=token,
        token_type="bearer",
        usuario=UsuarioDTO(
            id=usuario.id,
            login=usuario.login,
            nome=usuario.pessoa.razao_social if usuario.pessoa else usuario.login,
            perfil=usuario.perfil.nome if usuario.perfil else "COMUM",
            pessoa_id=usuario.pessoa_id,
            ativo=usuario.ativo,
            created_at=usuario.created_at,
        ),
    )


@router.get("/me", response_model=UsuarioDTO)
async def get_me(current_user: Usuario = Depends(get_current_user)) -> UsuarioDTO:
    """Retorna dados do usuário atualmente autenticado"""
    return UsuarioDTO(
        id=current_user.id,
        login=current_user.login,
        nome=current_user.pessoa.razao_social if current_user.pessoa else current_user.login,
        perfil=current_user.perfil.nome if current_user.perfil else "COMUM",
        pessoa_id=current_user.pessoa_id,
        ativo=current_user.ativo,
        created_at=current_user.created_at,
    )


@router.get("/perfis")
async def list_perfis(db: AsyncSession = Depends(get_db)):
    """Lista os perfis disponíveis no sistema"""
    stmt = select(Perfil).order_by(Perfil.id)
    res = await db.execute(stmt)
    return res.scalars().all()
