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
    DELETE /users/{user_id}           管理员   软删除用户
"""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Query

from app.api.deps import CurrentUser, SessionDep
from app.core.email import send_welcome_email
from app.core.exceptions import ForbiddenException, NotFoundException
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserRead,
    UserUpdate,
    UserUpdatePassword,
)
from app.services import user as user_service

router = APIRouter(prefix="/users", tags=["用户管理"])


# ---------------------------------------------------------------------------
# 公开接口
# ---------------------------------------------------------------------------


@router.post("/register", response_model=UserRead, summary="用户注册")
async def register(
    *,
    db: SessionDep,
    user_in: UserCreate,
    background_tasks: BackgroundTasks,
):
    """注册新用户"""
    user = user_service.create_user(db, user_in)

    # 异步发送欢迎邮件
    if user.email:
        background_tasks.add_task(
            send_welcome_email, to=user.email, username=user.username
        )

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
    db: SessionDep,
    current_user: CurrentUser,
    user_in: UserUpdate,
):
    """更新当前登录用户的个人信息"""
    return user_service.update_user(db, current_user, user_in)


@router.patch("/me/password", summary="修改密码")
async def update_current_user_password(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    password_in: UserUpdatePassword,
):
    """修改当前登录用户的密码"""
    user_service.update_password(db, current_user, password_in)
    return {"message": "密码修改成功"}


# ---------------------------------------------------------------------------
# 管理员接口
# ---------------------------------------------------------------------------


@router.get("", response_model=UserListResponse, summary="用户列表（管理员）")
async def list_users(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量"),
    keyword: Optional[str] = Query(None, description="搜索关键字"),
    status: Optional[int] = Query(None, description="状态筛选"),
):
    """获取用户分页列表（仅管理员）"""
    if not current_user.is_superuser:
        raise ForbiddenException(detail="权限不足，需要管理员权限")

    users, total = user_service.list_users(
        db, page=page, page_size=page_size, keyword=keyword, status=status
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
    db: SessionDep,
    current_user: CurrentUser,
    user_id: int,
):
    """按 ID 查询用户（仅管理员）"""
    if not current_user.is_superuser:
        raise ForbiddenException(detail="权限不足，需要管理员权限")

    user = user_service.get_user_by_id(db, user_id)
    if not user or user.is_deleted:
        raise NotFoundException(detail="用户不存在")
    return user


@router.delete("/{user_id}", summary="删除用户（管理员）")
async def delete_user(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    user_id: int,
):
    """软删除用户（仅管理员）"""
    if not current_user.is_superuser:
        raise ForbiddenException(detail="权限不足，需要管理员权限")

    user = user_service.get_user_by_id(db, user_id)
    if not user or user.is_deleted:
        raise NotFoundException(detail="用户不存在")
    if user.id == current_user.id:
        raise ForbiddenException(detail="不能删除自己")

    user_service.delete_user(db, user)
    return {"message": "用户已删除"}
