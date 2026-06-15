# app/api/routes/login.py

"""
认证路由 — 登录 / Token
"""

from __future__ import annotations

import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import SessionDep
from app.core import security
from app.core.config import settings
from app.core.logging import logger
from app.schemas.token import Token
from app.services import user as user_service

router = APIRouter(tags=["认证"])


@router.post("/login/access-token", response_model=Token, summary="登录获取 Token")
async def login_access_token(
    *,
    request: Request,
    db: SessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    OAuth2 兼容的登录接口，返回 JWT access token。
    """
    user = user_service.authenticate(db, form_data.username, form_data.password)

    # 更新登录信息
    client_ip = request.client.host if request.client else None
    user_service.update_login_info(db, user, ip=client_ip)

    access_token_expires = datetime.timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires
    )

    logger.info("用户登录成功 | id={} | username={} | ip={}", user.id, user.username, client_ip)

    return Token(access_token=access_token, token_type="bearer")