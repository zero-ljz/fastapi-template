# app/services/auth.py

"""基于 AsyncSession 的 Refresh Token 会话签发、轮换与撤销。"""

from datetime import datetime, timedelta
from uuid import uuid4

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import create_refresh_token, hash_refresh_token, utc_now
from app.models import RefreshSession, User


async def create_refresh_session(
    db: AsyncSession,
    *,
    user: User,
    client_type: str = "unknown",
    device_name: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
    family_id: str | None = None,
) -> str:
    raw_token = create_refresh_token()
    refresh_session = RefreshSession(
        user_id=user.id,
        family_id=family_id or str(uuid4()),
        token_hash=hash_refresh_token(raw_token),
        client_type=client_type,
        device_name=device_name,
        ip_address=ip_address,
        user_agent=user_agent,
        expires_at=utc_now() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
    )
    db.add(refresh_session)
    await db.flush()
    return raw_token


async def rotate_refresh_session(
    db: AsyncSession,
    *,
    raw_token: str,
    client_type: str | None = None,
    device_name: str | None = None,
    ip_address: str | None = None,
    user_agent: str | None = None,
) -> tuple[User, str]:
    token_hash = hash_refresh_token(raw_token)
    refresh_session = await db.scalar(
        select(RefreshSession)
        .options(selectinload(RefreshSession.user))
        .where(RefreshSession.token_hash == token_hash)
        .with_for_update()
    )
    if not refresh_session:
        raise UnauthorizedException(detail="无效的刷新令牌")

    now = utc_now()
    if refresh_session.revoked_at is not None:
        await _revoke_family(db, refresh_session.family_id, now)
        await db.flush()
        raise UnauthorizedException(detail="刷新令牌已失效，请重新登录")
    if refresh_session.expires_at <= now or not refresh_session.user.is_active:
        await _revoke_family(db, refresh_session.family_id, now)
        await db.flush()
        raise UnauthorizedException(detail="刷新令牌已过期，请重新登录")

    user = refresh_session.user
    refresh_session.revoked_at = now
    refresh_session.last_used_at = now
    new_token = create_refresh_token()
    db.add(
        RefreshSession(
            user_id=refresh_session.user_id,
            family_id=refresh_session.family_id,
            token_hash=hash_refresh_token(new_token),
            client_type=client_type or refresh_session.client_type,
            device_name=device_name or refresh_session.device_name,
            ip_address=ip_address,
            user_agent=user_agent,
            expires_at=now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS),
        )
    )
    await db.flush()
    return user, new_token


async def revoke_refresh_session(db: AsyncSession, raw_token: str) -> None:
    refresh_session = await db.scalar(
        select(RefreshSession).where(
            RefreshSession.token_hash == hash_refresh_token(raw_token)
        )
    )
    if refresh_session:
        await _revoke_family(db, refresh_session.family_id, utc_now())
        await db.flush()


async def revoke_all_user_sessions(db: AsyncSession, user_id: int) -> None:
    await db.execute(
        update(RefreshSession)
        .where(
            RefreshSession.user_id == user_id,
            RefreshSession.revoked_at.is_(None),
        )
        .values(revoked_at=utc_now())
    )
    await db.flush()


async def _revoke_family(
    db: AsyncSession, family_id: str, revoked_at: datetime
) -> None:
    await db.execute(
        update(RefreshSession)
        .where(
            RefreshSession.family_id == family_id,
            RefreshSession.revoked_at.is_(None),
        )
        .values(revoked_at=revoked_at)
    )
