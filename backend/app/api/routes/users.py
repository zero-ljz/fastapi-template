"""定义用户接口路由。"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.api.deps import (
    AsyncSessionDep,
    CurrentUser,
    get_current_active_superuser,
)
from app.core.exceptions import ForbiddenException, NotFoundException
from app.core.unit_of_work import unit_of_work
from app.models import User
from app.schemas.common import Message
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


# 公开接口


@router.post(
    "/register",
    response_model=UserRead,
    status_code=201,
    summary="用户注册",
)
async def register(
    *,
    db: AsyncSessionDep,
    user_in: UserCreate,
) -> User:
    """注册新用户。"""
    async with unit_of_work(db):
        user = await user_service.create_user(db, user_in)
    return user


# 当前用户接口


@router.get(
    "/me",
    response_model=UserRead,
    summary="获取当前用户信息",
)
async def get_current_user_info(current_user: CurrentUser) -> User:
    """获取当前登录用户的信息。"""
    return current_user


@router.patch(
    "/me",
    response_model=UserRead,
    summary="更新个人信息",
)
async def update_current_user(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    user_in: UserUpdate,
) -> User:
    """更新当前登录用户的个人信息。"""
    async with unit_of_work(db):
        user = await user_service.update_user(db, current_user, user_in)
    return user


@router.patch(
    "/me/password",
    summary="修改密码",
)
async def update_current_user_password(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    password_in: UserUpdatePassword,
) -> Message:
    """修改当前登录用户的密码。"""
    async with unit_of_work(db):
        await user_service.update_password(db, current_user, password_in)
        await auth_service.revoke_all_user_sessions(db, current_user.id)
    return Message(message="密码修改成功")


# 管理员接口


@router.get(
    "",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserListResponse,
    summary="用户列表（管理员）",
)
async def list_users(
    *,
    db: AsyncSessionDep,
    page: Annotated[int, Query(ge=1, description="页码")] = 1,
    page_size: Annotated[int, Query(ge=1, le=100, description="每页数量")] = 20,
    keyword: Annotated[str | None, Query(description="搜索关键字")] = None,
    is_active: Annotated[bool | None, Query(description="启用状态筛选")] = None,
) -> UserListResponse:
    """获取用户分页列表，仅限管理员。"""
    users, total = await user_service.list_users(
        db, page=page, page_size=page_size, keyword=keyword, is_active=is_active
    )
    return UserListResponse(
        items=[UserRead.model_validate(user) for user in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    response_model=UserRead,
    summary="查询用户（管理员）",
)
async def get_user(
    *,
    db: AsyncSessionDep,
    user_id: int,
) -> User:
    """按编号查询用户，仅限管理员。"""
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(
            detail="用户不存在",
            error_code="USER_NOT_FOUND",
        )
    return user


@router.delete(
    "/{user_id}",
    dependencies=[Depends(get_current_active_superuser)],
    summary="删除用户（管理员）",
)
async def delete_user(
    *,
    db: AsyncSessionDep,
    current_user: CurrentUser,
    user_id: int,
) -> Message:
    """删除用户，仅限管理员。"""
    user = await user_service.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundException(
            detail="用户不存在",
            error_code="USER_NOT_FOUND",
        )
    if user.id == current_user.id:
        raise ForbiddenException(detail="不能删除自己")

    async with unit_of_work(db):
        await user_service.delete_user(db, user)
    return Message(message="用户已删除")
