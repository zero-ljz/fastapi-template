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


class BaseAdmin(ModelView):
    page_size = 50
    page_size_options = [25, 50, 100, 200]


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


class UserAdmin(BaseAdmin, model=User):
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
    column_labels = {
        User.id: "ID",
        User.username: "用户名",
        User.email: "邮箱",
        User.phone: "手机号",
        User.nickname: "昵称",
        User.avatar_url: "头像",
        User.is_active: "已激活",
        User.is_superuser: "超级管理员",
        User.status: "状态",
        User.last_login_at: "最后登录时间",
        User.last_login_ip: "最后登录 IP",
        User.created_at: "创建时间",
        User.updated_at: "更新时间",
    }
    column_details_exclude_list = [
        User.password,
        User.user_roles,
        User.roles,
        User.workspace_users,
        User.operation_logs,
        User.notifications,
    ]
    form_excluded_columns = [
        "password",
        "roles",
        "workspace_users",
        "operation_logs",
        "notifications",
        "created_at",
        "updated_at",
    ]


class RoleAdmin(BaseAdmin, model=Role):
    name = "角色"
    name_plural = "角色"
    icon = "fa-solid fa-user-shield"
    column_list = [Role.id, Role.code, Role.name, Role.status, Role.sort_order]
    column_searchable_list = [Role.code, Role.name]
    column_sortable_list = [Role.id, Role.code, Role.sort_order]
    column_labels = {
        Role.id: "ID",
        Role.code: "角色编码",
        Role.name: "角色名称",
        Role.description: "描述",
        Role.sort_order: "排序",
        Role.status: "状态",
        Role.created_at: "创建时间",
        Role.updated_at: "更新时间",
    }
    column_details_exclude_list = [
        Role.user_roles,
        Role.role_permissions,
        Role.permissions,
    ]
    form_excluded_columns = [
        "permissions",
        "user_roles",
        "role_permissions",
        "created_at",
        "updated_at",
    ]


class PermissionAdmin(BaseAdmin, model=Permission):
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
    column_labels = {
        Permission.id: "ID",
        Permission.parent_id: "父级 ID",
        Permission.parent: "父级权限",
        Permission.code: "权限编码",
        Permission.name: "权限名称",
        Permission.type: "类型",
        Permission.path: "路径",
        Permission.method: "请求方法",
        Permission.icon: "图标",
        Permission.sort_order: "排序",
        Permission.status: "状态",
        Permission.created_at: "创建时间",
        Permission.updated_at: "更新时间",
    }
    column_details_exclude_list = [Permission.children, Permission.role_permissions]
    form_excluded_columns = ["children", "role_permissions", "created_at", "updated_at"]


class UserRoleAdmin(BaseAdmin, model=UserRole):
    name = "用户角色"
    name_plural = "用户角色"
    icon = "fa-solid fa-link"
    column_list = [
        UserRole.id,
        UserRole.user,
        UserRole.role,
        UserRole.created_at,
    ]
    column_sortable_list = [UserRole.id, UserRole.user_id, UserRole.role_id]
    column_labels = {
        UserRole.id: "ID",
        UserRole.user_id: "用户 ID",
        UserRole.user: "用户",
        UserRole.role_id: "角色 ID",
        UserRole.role: "角色",
        UserRole.created_at: "创建时间",
        UserRole.updated_at: "更新时间",
    }


class RolePermissionAdmin(BaseAdmin, model=RolePermission):
    name = "角色权限"
    name_plural = "角色权限"
    icon = "fa-solid fa-link"
    column_list = [
        RolePermission.id,
        RolePermission.role,
        RolePermission.permission,
        RolePermission.created_at,
    ]
    column_sortable_list = [
        RolePermission.id,
        RolePermission.role_id,
        RolePermission.permission_id,
    ]
    column_labels = {
        RolePermission.id: "ID",
        RolePermission.role_id: "角色 ID",
        RolePermission.role: "角色",
        RolePermission.permission_id: "权限 ID",
        RolePermission.permission: "权限",
        RolePermission.created_at: "创建时间",
        RolePermission.updated_at: "更新时间",
    }


class DictionaryAdmin(BaseAdmin, model=Dictionary):
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
    column_labels = {
        Dictionary.id: "ID",
        Dictionary.parent_id: "父级 ID",
        Dictionary.parent: "父级字典",
        Dictionary.code: "编码",
        Dictionary.label: "显示文本",
        Dictionary.value: "字典值",
        Dictionary.sort_order: "排序",
        Dictionary.status: "状态",
        Dictionary.remark: "备注",
        Dictionary.created_at: "创建时间",
        Dictionary.updated_at: "更新时间",
    }
    column_details_exclude_list = [Dictionary.children]
    form_excluded_columns = ["children", "created_at", "updated_at"]


class SystemConfigAdmin(BaseAdmin, model=SystemConfig):
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
    column_labels = {
        SystemConfig.id: "ID",
        SystemConfig.config_key: "配置键",
        SystemConfig.config_value: "配置值",
        SystemConfig.description: "描述",
        SystemConfig.is_public: "前端可见",
        SystemConfig.created_at: "创建时间",
        SystemConfig.updated_at: "更新时间",
    }
    form_excluded_columns = ["created_at", "updated_at"]


class OperationLogAdmin(BaseAdmin, model=OperationLog):
    name = "操作日志"
    name_plural = "操作日志"
    icon = "fa-solid fa-clipboard-list"
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [
        OperationLog.id,
        OperationLog.user,
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
    column_labels = {
        OperationLog.id: "ID",
        OperationLog.user_id: "操作人 ID",
        OperationLog.user: "操作人",
        OperationLog.username: "用户名",
        OperationLog.module: "模块",
        OperationLog.action: "操作",
        OperationLog.target_type: "目标类型",
        OperationLog.target_id: "目标 ID",
        OperationLog.ip: "IP",
        OperationLog.user_agent: "User-Agent",
        OperationLog.request_method: "请求方法",
        OperationLog.request_url: "请求路径",
        OperationLog.request_body: "请求参数",
        OperationLog.response_code: "响应码",
        OperationLog.detail: "详情",
        OperationLog.status: "状态",
        OperationLog.created_at: "操作时间",
    }


class WorkspaceAdmin(BaseAdmin, model=Workspace):
    name = "工作空间"
    name_plural = "工作空间"
    icon = "fa-solid fa-briefcase"
    column_list = [
        Workspace.id,
        Workspace.name,
        Workspace.code,
        Workspace.owner,
        Workspace.status,
        Workspace.created_at,
    ]
    column_searchable_list = [Workspace.name, Workspace.code]
    column_sortable_list = [Workspace.id, Workspace.code, Workspace.created_at]
    column_labels = {
        Workspace.id: "ID",
        Workspace.name: "空间名称",
        Workspace.code: "空间编码",
        Workspace.description: "描述",
        Workspace.logo_url: "Logo",
        Workspace.owner_id: "拥有者 ID",
        Workspace.owner: "拥有者",
        Workspace.status: "状态",
        Workspace.created_at: "创建时间",
        Workspace.updated_at: "更新时间",
    }
    column_details_exclude_list = [
        Workspace.workspace_users,
        Workspace.nodes,
        Workspace.items,
        Workspace.file_assets,
    ]
    form_excluded_columns = [
        "workspace_users",
        "nodes",
        "items",
        "file_assets",
        "created_at",
        "updated_at",
    ]


class WorkspaceUserAdmin(BaseAdmin, model=WorkspaceUser):
    name = "空间成员"
    name_plural = "空间成员"
    icon = "fa-solid fa-people-group"
    column_list = [
        WorkspaceUser.id,
        WorkspaceUser.workspace,
        WorkspaceUser.user,
        WorkspaceUser.role,
        WorkspaceUser.created_at,
    ]
    column_sortable_list = [
        WorkspaceUser.id,
        WorkspaceUser.workspace_id,
        WorkspaceUser.user_id,
    ]
    column_labels = {
        WorkspaceUser.id: "ID",
        WorkspaceUser.workspace_id: "空间 ID",
        WorkspaceUser.workspace: "工作空间",
        WorkspaceUser.user_id: "用户 ID",
        WorkspaceUser.user: "用户",
        WorkspaceUser.role: "空间角色",
        WorkspaceUser.created_at: "创建时间",
        WorkspaceUser.updated_at: "更新时间",
    }


class NodeAdmin(BaseAdmin, model=Node):
    name = "节点"
    name_plural = "节点"
    icon = "fa-solid fa-diagram-project"
    column_list = [
        Node.id,
        Node.workspace,
        Node.parent,
        Node.name,
        Node.type,
        Node.status,
        Node.sort_order,
    ]
    column_searchable_list = [Node.name, Node.type]
    column_sortable_list = [Node.id, Node.workspace_id, Node.sort_order]
    column_labels = {
        Node.id: "ID",
        Node.workspace_id: "空间 ID",
        Node.workspace: "工作空间",
        Node.parent_id: "父节点 ID",
        Node.parent: "父节点",
        Node.name: "节点名称",
        Node.type: "节点类型",
        Node.sort_order: "排序",
        Node.status: "状态",
        Node.metadata_json: "扩展属性",
        Node.created_by: "创建人 ID",
        Node.creator: "创建人",
        Node.created_at: "创建时间",
        Node.updated_at: "更新时间",
    }
    column_details_exclude_list = [Node.children, Node.items]
    form_excluded_columns = ["children", "items", "created_at", "updated_at"]


class ItemAdmin(BaseAdmin, model=Item):
    name = "条目"
    name_plural = "条目"
    icon = "fa-solid fa-list-check"
    column_list = [
        Item.id,
        Item.workspace,
        Item.node,
        Item.title,
        Item.type,
        Item.priority,
        Item.status,
        Item.due_date,
    ]
    column_searchable_list = [Item.title, Item.type, Item.status]
    column_sortable_list = [Item.id, Item.priority, Item.due_date]
    column_labels = {
        Item.id: "ID",
        Item.workspace_id: "空间 ID",
        Item.workspace: "工作空间",
        Item.node_id: "节点 ID",
        Item.node: "节点",
        Item.title: "标题",
        Item.content: "内容",
        Item.type: "条目类型",
        Item.priority: "优先级",
        Item.status: "状态",
        Item.assignee_id: "负责人 ID",
        Item.assignee: "负责人",
        Item.due_date: "截止时间",
        Item.metadata_json: "扩展属性",
        Item.created_by: "创建人 ID",
        Item.creator: "创建人",
        Item.created_at: "创建时间",
        Item.updated_at: "更新时间",
    }
    form_excluded_columns = ["created_at", "updated_at"]


class NotificationAdmin(BaseAdmin, model=Notification):
    name = "通知"
    name_plural = "通知"
    icon = "fa-solid fa-bell"
    column_list = [
        Notification.id,
        Notification.user,
        Notification.title,
        Notification.type,
        Notification.is_read,
        Notification.created_at,
    ]
    column_searchable_list = [
        Notification.title,
        Notification.content,
        Notification.type,
    ]
    column_sortable_list = [Notification.id, Notification.created_at]
    column_labels = {
        Notification.id: "ID",
        Notification.user_id: "接收人 ID",
        Notification.user: "接收人",
        Notification.title: "标题",
        Notification.content: "内容",
        Notification.type: "类型",
        Notification.is_read: "已读",
        Notification.read_at: "阅读时间",
        Notification.source_type: "来源类型",
        Notification.source_id: "来源 ID",
        Notification.sender_id: "发送人 ID",
        Notification.sender: "发送人",
        Notification.created_at: "创建时间",
        Notification.updated_at: "更新时间",
    }
    form_excluded_columns = ["created_at", "updated_at"]


class FileAssetAdmin(BaseAdmin, model=FileAsset):
    name = "文件资产"
    name_plural = "文件资产"
    icon = "fa-solid fa-file"
    column_list = [
        FileAsset.id,
        FileAsset.workspace,
        FileAsset.original_name,
        FileAsset.storage_type,
        FileAsset.file_size,
        FileAsset.uploader,
        FileAsset.created_at,
    ]
    column_searchable_list = [
        FileAsset.original_name,
        FileAsset.storage_path,
        FileAsset.mime_type,
        FileAsset.file_hash,
    ]
    column_sortable_list = [FileAsset.id, FileAsset.file_size, FileAsset.created_at]
    column_labels = {
        FileAsset.id: "ID",
        FileAsset.workspace_id: "空间 ID",
        FileAsset.workspace: "工作空间",
        FileAsset.original_name: "原始文件名",
        FileAsset.storage_path: "存储路径",
        FileAsset.file_size: "文件大小",
        FileAsset.mime_type: "MIME 类型",
        FileAsset.file_hash: "文件哈希",
        FileAsset.storage_type: "存储类型",
        FileAsset.target_type: "关联类型",
        FileAsset.target_id: "关联 ID",
        FileAsset.uploaded_by: "上传人 ID",
        FileAsset.uploader: "上传人",
        FileAsset.created_at: "创建时间",
        FileAsset.updated_at: "更新时间",
    }
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
