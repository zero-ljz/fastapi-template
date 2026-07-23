"""定义 FastAPI 依赖项。"""

from collections.abc import AsyncGenerator, Generator
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.db import AsyncSessionLocal, SessionLocal
from app.core.exceptions import ForbiddenException, UnauthorizedException
from app.core.logging import logger
from app.models import User
from app.schemas.token import TokenPayload

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


# 数据库会话依赖


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


# 当前用户依赖


async def get_current_user(db: AsyncSessionDep, token: TokenDep) -> User:
    """解析 JWT 令牌并返回当前用户。"""
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={"require": ["exp", "type"]},
        )
        token_data = TokenPayload.model_validate(payload)
        if token_data.type != "access":
            raise InvalidTokenError("令牌类型错误")
        if token_data.sub is None:
            raise InvalidTokenError("令牌缺少用户标识")
        user_id = int(token_data.sub)
    except (InvalidTokenError, ValidationError, ValueError, TypeError) as e:
        logger.warning("Token 验证失败: {}", str(e))
        raise UnauthorizedException(
            detail="无法验证凭据",
            error_code="INVALID_ACCESS_TOKEN",
        ) from e

    user = await db.get(User, user_id)
    if not user:
        raise UnauthorizedException(
            detail="无法验证凭据",
            error_code="INVALID_ACCESS_TOKEN",
        )
    if not user.is_active:
        raise ForbiddenException(
            detail="用户已被禁用",
            error_code="USER_DISABLED",
        )
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_current_active_superuser(current_user: CurrentUser) -> User:
    """要求当前用户是超级管理员。"""
    if not current_user.is_superuser:
        raise ForbiddenException(detail="权限不足，需要管理员权限")
    return current_user
