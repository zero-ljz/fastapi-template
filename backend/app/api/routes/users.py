# app/api/routes/users.py

"""
用户模块 API 路由

路由表:
    POST   /users/register           公开     用户注册
    GET    /users/me                  登录用户  获取当前用户
    PATCH  /users/me                  登录用户  更新个人信息
    PATCH  /users/me/password         登录用户  修改密码
    GET    /users/{user_id}           管理员   查询指定用户
    GET    /users                     管理员   用户分页列表
    DELETE /users/{user_id}           管理员   删除用户
"""

from __future__ import annotations

from fastapi import APIRouter, Query

from app.api.deps import AsyncSessionDep, CurrentUser
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.unit_of_work import unit_of_work
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserRead,
    UserUpdate,
    UserUpdatePassword,
)
from app.services import auth as auth_service
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["用户管理"])


# ---------------------------------------------------------------------------
# 公开接口
# ---------------------------------------------------------------------------


@router.post("/register", response_model=UserRead, status_code=201, summary="用户注册")
async def register(
    *,
    db: AsyncSessionDep,
    user_in: UserCreate,
):
    """注册新用户"""
    async with unit_of_work(db):
        user = await user_service.create_user(db, user_in)
    return user


# ---------------------------------------------------------------------------
# 当前用户接口
# ---------------------------------------------------------------------------


@router.get("/me", response_model=UserRead, summary="获取当前用户信息")
async def get_current_user_info(current_user: CurrentUser):
    """获取当前登录用户的信息"""
    return current_user


@router.patch("/me", response_model=UserRead, summary="更新个人信息")
async def update_current_user(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    user_in: UserUpdate,
):
    """更新当前登录用户的个人信息"""
    async with unit_of_work(db):
        user = await user_service.update_user(db, current_user, user_in)
    return user


@router.patch("/me/password", summary="修改密码")
async def update_current_user_password(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    password_in: UserUpdatePassword,
):
    """修改当前登录用户的密码"""
    async with unit_of_work(db):
        await user_service.update_password(db, current_user, password_in)
        await auth_service.revoke_all_user_sessions(db, current_user.id)
    return {"message": "密码修改成功"}


# ---------------------------------------------------------------------------
# 管理员接口
# ---------------------------------------------------------------------------


@router.get("", response_model=UserListResponse, summary="用户列表（管理员）")
async def list_users(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: str | None = Query(None, description="搜索关键字"),
    is_active: bool | None = Query(None, description="启用状态筛选"),
):
    """获取用户分页列表（仅管理员）"""
    if not current_user.is_superuser:
        raise ForbiddenException(detail="权限不足，需要管理员权限")

    users, total = await user_service.list_users(
        db, page=page, page_size=page_size, keyword=keyword, is_active=is_active
    )
    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{user_id}", response_model=UserRead, summary="查询用户（管理员）")
async def get_user(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    user_id: int,
):
    """按 ID 查询用户（仅管理员）"""
    if not current_user.is_superuser:
        raise ForbiddenException(detail="权限不足，需要管理员权限")

    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail="用户不存在")
    return user


@router.delete("/{user_id}", summary="删除用户（管理员）")
async def delete_user(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    user_id: int,
):
    """删除用户（仅管理员）"""
    if not current_user.is_superuser:
        raise ForbiddenException(detail="权限不足，需要管理员权限")

    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(detail="用户不存在")
    if user.id == current_user.id:
        raise ForbiddenException(detail="不能删除自己")

    async with unit_of_work(db):
        await user_service.delete_user(db, user)
    return {"message": "用户已删除"}
