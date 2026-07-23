"""基于 AsyncSession 的用户查询、注册、更新与认证逻辑。"""

from anyio import to_thread
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    UnauthorizedException,
)
from app.core.logging import logger
from app.core.security import get_password_hash, utc_now, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword


async def get_user_by_id(db: AsyncSession, user_id: int) -> User | None:
    return await db.get(User, user_id)


async def get_user_by_username(db: AsyncSession, username: str) -> User | None:
    return await db.scalar(select(User).where(User.username == username))


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    return await db.scalar(select(User).where(User.email == email.lower()))


async def list_users(
    db: AsyncSession,
    *,
    page: int = 1,
    page_size: int = 20,
    keyword: str | None = None,
    is_active: bool | None = None,
) -> tuple[list[User], int]:
    stmt = select(User)
    if keyword:
        like_pattern = f"%{keyword}%"
        stmt = stmt.where(
            or_(
                User.username.ilike(like_pattern),
                User.display_name.ilike(like_pattern),
                User.email.ilike(like_pattern),
            )
        )
    if is_active is not None:
        stmt = stmt.where(User.is_active.is_(is_active))

    total = await db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    stmt = stmt.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
    users = await db.scalars(stmt)
    return list(users.all()), total


async def create_user(db: AsyncSession, user_in: UserCreate) -> User:
    if user_in.username and await get_user_by_username(db, user_in.username):
        raise ConflictException(detail="用户名已存在")
    if await get_user_by_email(db, str(user_in.email)):
        raise ConflictException(detail="邮箱已被注册")

    hashed_password = await to_thread.run_sync(get_password_hash, user_in.password)
    user = User(
        email=str(user_in.email).lower(),
        username=user_in.username,
        hashed_password=hashed_password,
        display_name=user_in.display_name or user_in.username,
    )
    db.add(user)
    try:
        await db.flush()
    except IntegrityError as exc:
        raise ConflictException(detail="用户名或邮箱已存在") from exc
    await db.refresh(user)
    logger.info("新用户注册 | id={} | email={}", user.id, user.email)
    return user


async def update_user(db: AsyncSession, user: User, user_in: UserUpdate) -> User:
    update_data = user_in.model_dump(exclude_unset=True)
    if "email" in update_data:
        if not update_data["email"]:
            raise BadRequestException(detail="邮箱不能为空")
        email = str(update_data["email"]).lower()
        existing = await get_user_by_email(db, email)
        if existing and existing.id != user.id:
            raise ConflictException(detail="邮箱已被注册")
        update_data["email"] = email

    for field, value in update_data.items():
        setattr(user, field, value)
    try:
        await db.flush()
    except IntegrityError as exc:
        raise ConflictException(detail="用户信息已被占用") from exc
    await db.refresh(user)
    return user


async def update_password(
    db: AsyncSession, user: User, password_in: UserUpdatePassword
) -> None:
    valid, _ = await to_thread.run_sync(
        verify_password, password_in.old_password, user.hashed_password
    )
    if not valid:
        raise BadRequestException(detail="旧密码错误")
    if password_in.old_password == password_in.new_password:
        raise BadRequestException(detail="新密码不能与旧密码相同")
    user.hashed_password = await to_thread.run_sync(
        get_password_hash, password_in.new_password
    )
    await db.flush()


async def delete_user(db: AsyncSession, user: User) -> None:
    await db.delete(user)
    await db.flush()


async def authenticate(db: AsyncSession, identifier: str, password: str) -> User:
    user = await db.scalar(
        select(User).where(
            or_(User.username == identifier, User.email == identifier.lower())
        )
    )
    if not user:
        raise UnauthorizedException(detail="用户名、邮箱或密码错误")

    valid, updated_hash = await to_thread.run_sync(
        verify_password, password, user.hashed_password
    )
    if not valid:
        raise UnauthorizedException(detail="用户名、邮箱或密码错误")
    if not user.is_active:
        raise UnauthorizedException(detail="用户已被禁用")
    if updated_hash:
        user.hashed_password = updated_hash
        await db.flush()
    return user


async def update_login_info(db: AsyncSession, user: User) -> None:
    user.last_login_at = utc_now()
    await db.flush()
