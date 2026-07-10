# app/api/routes/login.py

"""登录、刷新与会话撤销。"""

import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, Header, Request
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import AsyncSessionDep, CurrentUser
from app.core import security
from app.core.config import settings
from app.core.logging import logger
from app.schemas.token import RefreshTokenRequest, RevokeTokenRequest, Token
from app.services import auth as auth_service
from app.services import user as user_service

router = APIRouter(tags=["认证"])


def _request_metadata(request: Request) -> tuple[str | None, str | None]:
    client_ip = request.client.host if request.client else None
    return client_ip, request.headers.get("user-agent")


def _create_access_token(user_id: int) -> str:
    return security.create_access_token(
        user_id,
        expires_delta=datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )


@router.post("/login/access-token", response_model=Token, summary="登录获取令牌")
async def login_access_token(
    *,
    request: Request,
    db: AsyncSessionDep,
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    x_client_type: Annotated[str | None, Header(max_length=32)] = None,
    x_device_name: Annotated[str | None, Header(max_length=128)] = None,
):
    user = await user_service.authenticate(db, form_data.username, form_data.password)
    await user_service.update_login_info(db, user)
    client_ip, user_agent = _request_metadata(request)
    refresh_token = await auth_service.create_refresh_session(
        db,
        user=user,
        client_type=x_client_type or "unknown",
        device_name=x_device_name,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    logger.info("用户登录成功 | id={} | ip={}", user.id, client_ip)
    return Token(
        access_token=_create_access_token(user.id),
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login/refresh", response_model=Token, summary="刷新访问令牌")
async def refresh_access_token(
    *, request: Request, db: AsyncSessionDep, token_in: RefreshTokenRequest
):
    client_ip, user_agent = _request_metadata(request)
    user, refresh_token = await auth_service.rotate_refresh_session(
        db,
        raw_token=token_in.refresh_token,
        client_type=token_in.client_type,
        device_name=token_in.device_name,
        ip_address=client_ip,
        user_agent=user_agent,
    )
    return Token(
        access_token=_create_access_token(user.id),
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/login/logout", summary="退出当前设备")
async def logout(*, db: AsyncSessionDep, token_in: RevokeTokenRequest):
    await auth_service.revoke_refresh_session(db, token_in.refresh_token)
    return {"message": "已退出登录"}


@router.post("/login/logout-all", summary="退出全部设备")
async def logout_all(*, db: AsyncSessionDep, current_user: CurrentUser):
    await auth_service.revoke_all_user_sessions(db, current_user.id)
    return {"message": "已退出全部设备"}
