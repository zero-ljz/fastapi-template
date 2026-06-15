# app/api/deps.py

"""
FastAPI 依赖注入
"""

from collections.abc import Generator, AsyncGenerator
from typing import Annotated

from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import jwt
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError

from app.core.db import SessionLocal, AsyncSessionLocal
from app.core import security
from app.core.config import settings
from app.core.logging import logger
from app.models import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


# ---------------------------------------------------------------------------
# 数据库会话
# ---------------------------------------------------------------------------

def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


# ---------------------------------------------------------------------------
# 当前用户
# ---------------------------------------------------------------------------

def get_current_user(db: SessionDep, token: TokenDep) -> User:
    """从 JWT Token 解析并返回当前用户"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)
    except (InvalidTokenError, ValidationError) as e:
        logger.warning("Token 验证失败: {}", str(e))
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无法验证凭据",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token_data.sub is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 Token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # sub 存储的是 user.id
    user = db.get(User, int(token_data.sub))
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="用户已被禁用")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    """要求当前用户是超级管理员"""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="权限不足，需要管理员权限"
        )
    return current_user
