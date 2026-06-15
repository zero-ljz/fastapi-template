"""
SQLAdmin 后台管理入口。
"""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from sqladmin.widgets import BooleanInputWidget
from starlette.requests import Request

from app.core.config import settings
from app.core.db import SessionLocal, engine
from app.core.security import verify_password
from app.models import (
    Dictionary,
    FileAsset,
    Item,
    Node,
    Notification,
    OperationLog,
    Permission,
    Role,
    RolePermission,
    SystemConfig,
    User,
    UserRole,
    Workspace,
    WorkspaceUser,
)
from app.services.user import get_user_by_username

if not hasattr(BooleanInputWidget, "validation_attrs"):
    BooleanInputWidget.validation_attrs = ["required", "disabled"]


class AdminAuth(AuthenticationBackend):
    """使用系统内已有超级管理员账号登录 SQLAdmin。"""

    async def login(self, request: Request) -> bool:
        form = await request.form()
        username = str(form.get("username", ""))
        password = str(form.get("password", ""))

        with SessionLocal() as db:
            user = get_user_by_username(db, username)
            if not user or not user.is_active or not user.is_superuser:
                return False

            valid, _ = verify_password(password, user.password)
            if not valid:
                return False

            request.session.update({"admin_user_id": user.id})
            return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        user_id = request.session.get("admin_user_id")
        if not user_id:
            return False

        with SessionLocal() as db:
            user = db.get(User, int(user_id))
            return bool(user and user.is_active and user.is_superuser)


class UserAdmin(ModelView, model=User):
    name = "用户"
    name_plural = "用户"
    icon = "fa-solid fa-users"
    can_create = False
    column_list = [
        User.id,
        User.username,
        User.email,
        User.nickname,
        User.is_active,
        User.is_superuser,
        User.status,
        User.created_at,
    ]
    column_searchable_list = [User.username, User.email, User.nickname]
    column_sortable_list = [User.id, User.username, User.created_at]
    column_details_exclude_list = [User.password]
    form_excluded_columns = [
        "password",
        "roles",
        "workspace_users",
        "operation_logs",
        "notifications",
        "created_at",
        "updated_at",
    ]


class RoleAdmin(ModelView, model=Role):
    name = "角色"
    name_plural = "角色"
    icon = "fa-solid fa-user-shield"
    column_list = [Role.id, Role.code, Role.name, Role.status, Role.sort_order]
    column_searchable_list = [Role.code, Role.name]
    column_sortable_list = [Role.id, Role.code, Role.sort_order]
    form_excluded_columns = [
        "permissions",
        "user_roles",
        "role_permissions",
        "created_at",
        "updated_at",
    ]


class PermissionAdmin(ModelView, model=Permission):
    name = "权限"
    name_plural = "权限"
    icon = "fa-solid fa-key"
    column_list = [
        Permission.id,
        Permission.code,
        Permission.name,
        Permission.type,
        Permission.path,
        Permission.method,
        Permission.status,
    ]
    column_searchable_list = [Permission.code, Permission.name, Permission.path]
    column_sortable_list = [Permission.id, Permission.code, Permission.sort_order]
    form_excluded_columns = ["children", "role_permissions", "created_at", "updated_at"]


class UserRoleAdmin(ModelView, model=UserRole):
    name = "用户角色"
    name_plural = "用户角色"
    icon = "fa-solid fa-link"
    column_list = [
        UserRole.id,
        UserRole.user_id,
        UserRole.role_id,
        UserRole.created_at,
    ]
    column_sortable_list = [UserRole.id, UserRole.user_id, UserRole.role_id]


class RolePermissionAdmin(ModelView, model=RolePermission):
    name = "角色权限"
    name_plural = "角色权限"
    icon = "fa-solid fa-link"
    column_list = [
        RolePermission.id,
        RolePermission.role_id,
        RolePermission.permission_id,
        RolePermission.created_at,
    ]
    column_sortable_list = [
        RolePermission.id,
        RolePermission.role_id,
        RolePermission.permission_id,
    ]


class DictionaryAdmin(ModelView, model=Dictionary):
    name = "数据字典"
    name_plural = "数据字典"
    icon = "fa-solid fa-book"
    column_list = [
        Dictionary.id,
        Dictionary.parent_id,
        Dictionary.code,
        Dictionary.label,
        Dictionary.value,
        Dictionary.status,
        Dictionary.sort_order,
    ]
    column_searchable_list = [Dictionary.code, Dictionary.label, Dictionary.value]
    column_sortable_list = [Dictionary.id, Dictionary.code, Dictionary.sort_order]
    form_excluded_columns = ["children", "created_at", "updated_at"]


class SystemConfigAdmin(ModelView, model=SystemConfig):
    name = "系统配置"
    name_plural = "系统配置"
    icon = "fa-solid fa-gear"
    column_list = [
        SystemConfig.id,
        SystemConfig.config_key,
        SystemConfig.config_value,
        SystemConfig.is_public,
    ]
    column_searchable_list = [SystemConfig.config_key, SystemConfig.config_value]
    column_sortable_list = [SystemConfig.id, SystemConfig.config_key]
    form_excluded_columns = ["created_at", "updated_at"]


class OperationLogAdmin(ModelView, model=OperationLog):
    name = "操作日志"
    name_plural = "操作日志"
    icon = "fa-solid fa-clipboard-list"
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [
        OperationLog.id,
        OperationLog.user_id,
        OperationLog.username,
        OperationLog.module,
        OperationLog.action,
        OperationLog.status,
        OperationLog.created_at,
    ]
    column_searchable_list = [
        OperationLog.username,
        OperationLog.module,
        OperationLog.action,
        OperationLog.target_type,
    ]
    column_sortable_list = [OperationLog.id, OperationLog.created_at]


class WorkspaceAdmin(ModelView, model=Workspace):
    name = "工作空间"
    name_plural = "工作空间"
    icon = "fa-solid fa-briefcase"
    column_list = [
        Workspace.id,
        Workspace.name,
        Workspace.code,
        Workspace.owner_id,
        Workspace.status,
        Workspace.created_at,
    ]
    column_searchable_list = [Workspace.name, Workspace.code]
    column_sortable_list = [Workspace.id, Workspace.code, Workspace.created_at]
    form_excluded_columns = [
        "workspace_users",
        "nodes",
        "items",
        "file_assets",
        "created_at",
        "updated_at",
    ]


class WorkspaceUserAdmin(ModelView, model=WorkspaceUser):
    name = "空间成员"
    name_plural = "空间成员"
    icon = "fa-solid fa-people-group"
    column_list = [
        WorkspaceUser.id,
        WorkspaceUser.workspace_id,
        WorkspaceUser.user_id,
        WorkspaceUser.role,
        WorkspaceUser.created_at,
    ]
    column_sortable_list = [WorkspaceUser.id, WorkspaceUser.workspace_id, WorkspaceUser.user_id]


class NodeAdmin(ModelView, model=Node):
    name = "节点"
    name_plural = "节点"
    icon = "fa-solid fa-diagram-project"
    column_list = [
        Node.id,
        Node.workspace_id,
        Node.parent_id,
        Node.name,
        Node.type,
        Node.status,
        Node.sort_order,
    ]
    column_searchable_list = [Node.name, Node.type]
    column_sortable_list = [Node.id, Node.workspace_id, Node.sort_order]
    form_excluded_columns = ["children", "items", "created_at", "updated_at"]


class ItemAdmin(ModelView, model=Item):
    name = "条目"
    name_plural = "条目"
    icon = "fa-solid fa-list-check"
    column_list = [
        Item.id,
        Item.workspace_id,
        Item.node_id,
        Item.title,
        Item.type,
        Item.priority,
        Item.status,
        Item.due_date,
    ]
    column_searchable_list = [Item.title, Item.type, Item.status]
    column_sortable_list = [Item.id, Item.priority, Item.due_date]
    form_excluded_columns = ["created_at", "updated_at"]


class NotificationAdmin(ModelView, model=Notification):
    name = "通知"
    name_plural = "通知"
    icon = "fa-solid fa-bell"
    column_list = [
        Notification.id,
        Notification.user_id,
        Notification.title,
        Notification.type,
        Notification.is_read,
        Notification.created_at,
    ]
    column_searchable_list = [Notification.title, Notification.content, Notification.type]
    column_sortable_list = [Notification.id, Notification.created_at]
    form_excluded_columns = ["created_at", "updated_at"]


class FileAssetAdmin(ModelView, model=FileAsset):
    name = "文件资产"
    name_plural = "文件资产"
    icon = "fa-solid fa-file"
    column_list = [
        FileAsset.id,
        FileAsset.workspace_id,
        FileAsset.original_name,
        FileAsset.storage_type,
        FileAsset.file_size,
        FileAsset.uploaded_by,
        FileAsset.created_at,
    ]
    column_searchable_list = [
        FileAsset.original_name,
        FileAsset.storage_path,
        FileAsset.mime_type,
        FileAsset.file_hash,
    ]
    column_sortable_list = [FileAsset.id, FileAsset.file_size, FileAsset.created_at]
    form_excluded_columns = ["created_at", "updated_at"]


def register_admin(app: FastAPI) -> Admin:
    @app.get("/admin", include_in_schema=False)
    async def redirect_to_admin() -> RedirectResponse:
        return RedirectResponse(url="/admin/")

    admin = Admin(
        app,
        engine,
        title=f"{settings.PROJECT_NAME} Admin",
        authentication_backend=AdminAuth(secret_key=settings.SECRET_KEY),
    )

    for view in (
        UserAdmin,
        RoleAdmin,
        PermissionAdmin,
        UserRoleAdmin,
        RolePermissionAdmin,
        DictionaryAdmin,
        SystemConfigAdmin,
        OperationLogAdmin,
        WorkspaceAdmin,
        WorkspaceUserAdmin,
        NodeAdmin,
        ItemAdmin,
        NotificationAdmin,
        FileAssetAdmin,
    ):
        admin.add_view(view)

    return admin
