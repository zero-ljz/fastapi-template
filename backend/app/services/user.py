# app/services/user.py

"""
用户 Service 层 — 封装业务逻辑，供 API 路由调用
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.exceptions import (
    BadRequestException,
    ConflictException,
    NotFoundException,
    UnauthorizedException,
)
from app.core.logging import logger
from app.core.security import get_password_hash, verify_password
from app.models import User
from app.schemas.user import UserCreate, UserUpdate, UserUpdatePassword, UserAdminUpdate


# ---------------------------------------------------------------------------
# 查询
# ---------------------------------------------------------------------------

def get_user_by_id(db: Session, user_id: int) -> Optional[User]:
    """按 ID 查询用户"""
    return db.get(User, user_id)


def get_user_by_username(db: Session, username: str) -> Optional[User]:
    """按用户名查询用户"""
    stmt = select(User).where(User.username == username, User.is_deleted == False)
    return db.execute(stmt).scalar_one_or_none()


def get_user_by_email(db: Session, email: str) -> Optional[User]:
    """按邮箱查询用户"""
    stmt = select(User).where(User.email == email, User.is_deleted == False)
    return db.execute(stmt).scalar_one_or_none()


def list_users(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    keyword: Optional[str] = None,
    status: Optional[int] = None,
) -> tuple[list[User], int]:
    """分页查询用户列表，返回 (用户列表, 总数)"""
    stmt = select(User).where(User.is_deleted == False)

    if keyword:
        like_pattern = f"%{keyword}%"
        stmt = stmt.where(
            (User.username.ilike(like_pattern))
            | (User.nickname.ilike(like_pattern))
            | (User.email.ilike(like_pattern))
        )
    if status is not None:
        stmt = stmt.where(User.status == status)

    # 总数
    count_stmt = select(func.count()).select_from(stmt.subquery())
    total = db.execute(count_stmt).scalar() or 0

    # 分页
    stmt = stmt.order_by(User.id.desc()).offset((page - 1) * page_size).limit(page_size)
    users = list(db.execute(stmt).scalars().all())

    return users, total


# ---------------------------------------------------------------------------
# 创建
# ---------------------------------------------------------------------------

def create_user(db: Session, user_in: UserCreate) -> User:
    """创建用户（注册）"""
    # 唯一性检查
    if get_user_by_username(db, user_in.username):
        raise ConflictException(detail="用户名已存在")
    if user_in.email and get_user_by_email(db, user_in.email):
        raise ConflictException(detail="邮箱已被注册")

    user = User(
        username=user_in.username,
        password=get_password_hash(user_in.password),
        email=user_in.email,
        nickname=user_in.nickname or user_in.username,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info("新用户注册 | id={} | username={}", user.id, user.username)
    return user


# ---------------------------------------------------------------------------
# 更新
# ---------------------------------------------------------------------------

def update_user(db: Session, user: User, user_in: UserUpdate) -> User:
    """更新用户信息"""
    update_data = user_in.model_dump(exclude_unset=True)

    # 邮箱唯一性检查
    if "email" in update_data and update_data["email"]:
        existing = get_user_by_email(db, update_data["email"])
        if existing and existing.id != user.id:
            raise ConflictException(detail="邮箱已被注册")

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    logger.info("用户信息更新 | id={} | fields={}", user.id, list(update_data.keys()))
    return user


def admin_update_user(db: Session, user: User, user_in: UserAdminUpdate) -> User:
    """管理员更新用户"""
    update_data = user_in.model_dump(exclude_unset=True)

    if "email" in update_data and update_data["email"]:
        existing = get_user_by_email(db, update_data["email"])
        if existing and existing.id != user.id:
            raise ConflictException(detail="邮箱已被注册")

    for field, value in update_data.items():
        setattr(user, field, value)

    db.commit()
    db.refresh(user)
    logger.info("管理员更新用户 | id={} | fields={}", user.id, list(update_data.keys()))
    return user


def update_password(db: Session, user: User, password_in: UserUpdatePassword) -> None:
    """修改密码"""
    valid, _ = verify_password(password_in.old_password, user.password)
    if not valid:
        raise BadRequestException(detail="旧密码错误")

    user.password = get_password_hash(password_in.new_password)
    db.commit()
    logger.info("用户修改密码 | id={}", user.id)


# ---------------------------------------------------------------------------
# 删除
# ---------------------------------------------------------------------------

def delete_user(db: Session, user: User) -> None:
    """软删除用户"""
    user.is_deleted = True
    user.is_active = False
    db.commit()
    logger.info("用户已删除 | id={} | username={}", user.id, user.username)


# ---------------------------------------------------------------------------
# 认证
# ---------------------------------------------------------------------------

def authenticate(db: Session, username: str, password: str) -> User:
    """验证用户名 + 密码，返回用户对象"""
    user = get_user_by_username(db, username)
    if not user:
        raise UnauthorizedException(detail="用户名或密码错误")

    valid, updated_hash = verify_password(password, user.password)
    if not valid:
        raise UnauthorizedException(detail="用户名或密码错误")

    # 如果密码哈希算法升级，自动更新存储的哈希
    if updated_hash:
        user.password = updated_hash
        db.commit()

    if not user.is_active:
        raise UnauthorizedException(detail="用户已被禁用")

    return user


def update_login_info(db: Session, user: User, ip: Optional[str] = None) -> None:
    """更新最后登录信息"""
    user.last_login_at = datetime.now()
    user.last_login_ip = ip
    db.commit()
