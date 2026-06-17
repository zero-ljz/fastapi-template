"""
SQLAlchemy 2.0 ORM Models
Domains:
  - Auth & RBAC : User, Role, Permission, RolePermission, UserRole
  - System      : Dictionary, SystemConfig, OperationLog
  - Workspace   : Workspace, WorkspaceUser
  - Business    : Node, Item, Notification, FileAsset
"""

from __future__ import annotations

import enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
)


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Declarative base with common audit columns."""
    pass


class TimestampMixin:
    """created_at / updated_at auto-managed by the database."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
        comment="创建时间",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
        comment="更新时间",
    )


class SoftDeleteMixin:
    """Logical-delete support."""

    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        server_default="0",
        nullable=False,
        comment="逻辑删除 0-未删除 1-已删除",
    )


# ===================================================================
# Auth & RBAC
# ===================================================================

class User(TimestampMixin, SoftDeleteMixin, Base):
    """系统用户"""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="用户名")
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True, nullable=True, comment="邮箱")
    phone: Mapped[Optional[str]] = mapped_column(String(32), unique=True, nullable=True, comment="手机号")
    password: Mapped[str] = mapped_column(String(255), nullable=False, comment="密码哈希")
    nickname: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="昵称")
    avatar_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="头像URL")
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, comment="是否激活")
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, comment="是否超级用户")
    status: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
        comment="状态 0-禁用 1-启用",
    )
    last_login_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="最后登录时间")
    last_login_ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="最后登录IP")

    # --- relationships ---
    user_roles: Mapped[List["UserRole"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    roles: Mapped[List["Role"]] = relationship(
        secondary="user_role", viewonly=True, lazy="selectin",
    )
    workspace_users: Mapped[List["WorkspaceUser"]] = relationship(back_populates="user", cascade="all, delete-orphan")
    operation_logs: Mapped[List["OperationLog"]] = relationship(back_populates="user")
    notifications: Mapped[List["Notification"]] = relationship(
        back_populates="user", foreign_keys="Notification.user_id",
    )

    __table_args__ = (
        Index("ix_user_status", "status"),
        {"comment": "用户表"},
    )

    def __str__(self) -> str:
        return self.nickname or self.username or f"用户#{self.id}"


class Role(TimestampMixin, SoftDeleteMixin, Base):
    """角色"""

    __tablename__ = "role"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="角色编码")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="角色名称")
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="描述")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", comment="排序")
    status: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
        comment="状态 0-禁用 1-启用",
    )

    # --- relationships ---
    user_roles: Mapped[List["UserRole"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    role_permissions: Mapped[List["RolePermission"]] = relationship(back_populates="role", cascade="all, delete-orphan")
    permissions: Mapped[List["Permission"]] = relationship(
        secondary="role_permission", viewonly=True, lazy="selectin",
    )

    __table_args__ = (
        {"comment": "角色表"},
    )

    def __str__(self) -> str:
        name = self.name or f"角色#{self.id}"
        return f"{name}({self.code})" if self.code else name


class Permission(TimestampMixin, Base):
    """权限（菜单 / 按钮 / API）"""

    __tablename__ = "permission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("permission.id", ondelete="SET NULL"), nullable=True, comment="父级ID",
    )
    code: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment="权限编码")
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="权限名称")
    type: Mapped[str] = mapped_column(
        String(16), nullable=False, comment="权限类型 menu / button / api",
    )
    path: Mapped[Optional[str]] = mapped_column(String(256), nullable=True, comment="前端路由/接口路径")
    method: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, comment="HTTP Method (GET/POST/...)")
    icon: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, comment="图标")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", comment="排序")
    status: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
        comment="状态 0-禁用 1-启用",
    )

    # --- relationships ---
    children: Mapped[List["Permission"]] = relationship(back_populates="parent", lazy="selectin")
    parent: Mapped[Optional["Permission"]] = relationship(
        back_populates="children", remote_side=[id],
    )
    role_permissions: Mapped[List["RolePermission"]] = relationship(back_populates="permission")

    __table_args__ = (
        Index("ix_permission_parent_id", "parent_id"),
        Index("ix_permission_type", "type"),
        {"comment": "权限表"},
    )

    def __str__(self) -> str:
        name = self.name or f"权限#{self.id}"
        return f"{name}({self.code})" if self.code else name


class RolePermission(TimestampMixin, Base):
    """角色-权限 关联表"""

    __tablename__ = "role_permission"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("role.id", ondelete="CASCADE"), nullable=False,
    )
    permission_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("permission.id", ondelete="CASCADE"), nullable=False,
    )

    # --- relationships ---
    role: Mapped["Role"] = relationship(back_populates="role_permissions")
    permission: Mapped["Permission"] = relationship(back_populates="role_permissions")

    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
        Index("ix_role_permission_role_id", "role_id"),
        Index("ix_role_permission_permission_id", "permission_id"),
        {"comment": "角色-权限关联表"},
    )

    def __str__(self) -> str:
        return f"{self.role} - {self.permission}"


class UserRole(TimestampMixin, Base):
    """用户-角色 关联表"""

    __tablename__ = "user_role"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False,
    )
    role_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("role.id", ondelete="CASCADE"), nullable=False,
    )

    # --- relationships ---
    user: Mapped["User"] = relationship(back_populates="user_roles")
    role: Mapped["Role"] = relationship(back_populates="user_roles")

    __table_args__ = (
        UniqueConstraint("user_id", "role_id", name="uq_user_role"),
        Index("ix_user_role_user_id", "user_id"),
        Index("ix_user_role_role_id", "role_id"),
        {"comment": "用户-角色关联表"},
    )

    def __str__(self) -> str:
        return f"{self.user} - {self.role}"


# ===================================================================
# System
# ===================================================================

class Dictionary(TimestampMixin, SoftDeleteMixin, Base):
    """数据字典 — 两级结构: 字典类型 (parent_id=NULL) → 字典条目"""

    __tablename__ = "dictionary"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("dictionary.id", ondelete="CASCADE"), nullable=True,
        comment="父级ID, NULL 表示字典类型",
    )
    code: Mapped[str] = mapped_column(String(128), nullable=False, comment="编码 / 字典类型编码")
    label: Mapped[str] = mapped_column(String(256), nullable=False, comment="显示文本")
    value: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="字典值")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", comment="排序")
    status: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
        comment="状态 0-禁用 1-启用",
    )
    remark: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="备注")

    # --- relationships ---
    children: Mapped[List["Dictionary"]] = relationship(back_populates="parent", lazy="selectin")
    parent: Mapped[Optional["Dictionary"]] = relationship(
        back_populates="children", remote_side=[id],
    )

    __table_args__ = (
        Index("ix_dictionary_parent_id", "parent_id"),
        Index("ix_dictionary_code", "code"),
        {"comment": "数据字典表"},
    )

    def __str__(self) -> str:
        label = self.label or f"字典#{self.id}"
        return f"{label}({self.code})" if self.code else label


class SystemConfig(TimestampMixin, Base):
    """系统配置 (Key-Value)"""

    __tablename__ = "system_config"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    config_key: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, comment="配置键")
    config_value: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="配置值 (JSON / 纯文本)")
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="描述")
    is_public: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False,
        comment="是否前端可见",
    )

    __table_args__ = (
        {"comment": "系统配置表"},
    )

    def __str__(self) -> str:
        return self.config_key or f"配置#{self.id}"


class OperationLog(Base):
    """操作日志 — 仅追加, 不做软删除"""

    __tablename__ = "operation_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="操作人ID",
    )
    username: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="操作人用户名(冗余)")
    module: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="模块")
    action: Mapped[str] = mapped_column(String(64), nullable=False, comment="操作类型")
    target_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="目标资源类型")
    target_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="目标资源ID")
    ip: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="请求IP")
    user_agent: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="User-Agent")
    request_method: Mapped[Optional[str]] = mapped_column(String(16), nullable=True, comment="HTTP Method")
    request_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="请求路径")
    request_body: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="请求参数(脱敏)")
    response_code: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, comment="响应状态码")
    detail: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="详情 / 备注")
    status: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
        comment="执行结果 0-失败 1-成功",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), nullable=False, comment="操作时间",
    )

    # --- relationships ---
    user: Mapped[Optional["User"]] = relationship(back_populates="operation_logs")

    __table_args__ = (
        Index("ix_oplog_user_id", "user_id"),
        Index("ix_oplog_action", "action"),
        Index("ix_oplog_target", "target_type", "target_id"),
        Index("ix_oplog_created_at", "created_at"),
        {"comment": "操作日志表"},
    )

    def __str__(self) -> str:
        actor = self.username or self.user_id or "匿名"
        return f"{actor} {self.action} #{self.id}"


# ===================================================================
# Workspace
# ===================================================================

class Workspace(TimestampMixin, SoftDeleteMixin, Base):
    """工作空间 / 团队"""

    __tablename__ = "workspace"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False, comment="空间名称")
    code: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, comment="空间编码(URL slug)")
    description: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="描述")
    logo_url: Mapped[Optional[str]] = mapped_column(String(512), nullable=True, comment="Logo URL")
    owner_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="RESTRICT"), nullable=False, comment="拥有者",
    )
    status: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
        comment="状态 0-归档 1-活跃",
    )

    # --- relationships ---
    owner: Mapped["User"] = relationship(foreign_keys=[owner_id])
    workspace_users: Mapped[List["WorkspaceUser"]] = relationship(
        back_populates="workspace", cascade="all, delete-orphan",
    )
    nodes: Mapped[List["Node"]] = relationship(back_populates="workspace")
    items: Mapped[List["Item"]] = relationship(back_populates="workspace")
    file_assets: Mapped[List["FileAsset"]] = relationship(back_populates="workspace")

    __table_args__ = (
        Index("ix_workspace_owner_id", "owner_id"),
        {"comment": "工作空间表"},
    )

    def __str__(self) -> str:
        name = self.name or f"空间#{self.id}"
        return f"{name}({self.code})" if self.code else name


class WorkspaceUserRole(str, enum.Enum):
    """工作空间内角色"""
    OWNER = "owner"
    ADMIN = "admin"
    MEMBER = "member"
    VIEWER = "viewer"


class WorkspaceUser(TimestampMixin, Base):
    """工作空间-用户 关联 (含空间内角色)"""

    __tablename__ = "workspace_user"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False,
    )
    role: Mapped[str] = mapped_column(
        String(16), default=WorkspaceUserRole.MEMBER.value,
        server_default=WorkspaceUserRole.MEMBER.value,
        nullable=False, comment="空间角色 owner/admin/member/viewer",
    )

    # --- relationships ---
    workspace: Mapped["Workspace"] = relationship(back_populates="workspace_users")
    user: Mapped["User"] = relationship(back_populates="workspace_users")

    __table_args__ = (
        UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),
        Index("ix_workspace_user_workspace_id", "workspace_id"),
        Index("ix_workspace_user_user_id", "user_id"),
        {"comment": "工作空间-用户关联表"},
    )

    def __str__(self) -> str:
        return f"{self.workspace} - {self.user}({self.role})"


# ===================================================================
# Business
# ===================================================================

class Node(TimestampMixin, SoftDeleteMixin, Base):
    """节点 — 树形业务对象 (文件夹 / 分类 / 流程节点等)"""

    __tablename__ = "node"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False, comment="所属工作空间",
    )
    parent_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("node.id", ondelete="SET NULL"), nullable=True, comment="父节点",
    )
    name: Mapped[str] = mapped_column(String(256), nullable=False, comment="节点名称")
    type: Mapped[str] = mapped_column(String(32), nullable=False, comment="节点类型")
    sort_order: Mapped[int] = mapped_column(Integer, default=0, server_default="0", comment="排序")
    status: Mapped[int] = mapped_column(
        Integer, default=1, server_default="1", nullable=False,
        comment="状态 0-禁用 1-启用",
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="扩展属性 (JSON)")
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="创建人",
    )

    # --- relationships ---
    workspace: Mapped["Workspace"] = relationship(back_populates="nodes")
    parent: Mapped[Optional["Node"]] = relationship(
        back_populates="children", remote_side=[id],
    )
    children: Mapped[List["Node"]] = relationship(back_populates="parent", lazy="selectin")
    creator: Mapped[Optional["User"]] = relationship(foreign_keys=[created_by])
    items: Mapped[List["Item"]] = relationship(back_populates="node")

    __table_args__ = (
        Index("ix_node_workspace_id", "workspace_id"),
        Index("ix_node_parent_id", "parent_id"),
        Index("ix_node_type", "type"),
        {"comment": "节点表"},
    )

    def __str__(self) -> str:
        name = self.name or f"节点#{self.id}"
        return f"{name}({self.type})" if self.type else name


class Item(TimestampMixin, SoftDeleteMixin, Base):
    """条目 — 业务数据主体 (任务 / 文档 / 记录 等)"""

    __tablename__ = "item"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workspace_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("workspace.id", ondelete="CASCADE"), nullable=False, comment="所属工作空间",
    )
    node_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("node.id", ondelete="SET NULL"), nullable=True, comment="所属节点",
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False, comment="标题")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="正文 / 富文本")
    type: Mapped[str] = mapped_column(String(32), nullable=False, comment="条目类型")
    priority: Mapped[int] = mapped_column(
        Integer, default=0, server_default="0", nullable=False, comment="优先级 0-无 1-低 2-中 3-高 4-紧急",
    )
    status: Mapped[str] = mapped_column(
        String(32), default="open", server_default="open", nullable=False,
        comment="状态 (open / in_progress / done / closed …)",
    )
    assignee_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="负责人",
    )
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="截止时间")
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="扩展属性 (JSON)")
    created_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="创建人",
    )

    # --- relationships ---
    workspace: Mapped["Workspace"] = relationship(back_populates="items")
    node: Mapped[Optional["Node"]] = relationship(back_populates="items")
    assignee: Mapped[Optional["User"]] = relationship(foreign_keys=[assignee_id])
    creator: Mapped[Optional["User"]] = relationship(foreign_keys=[created_by])

    __table_args__ = (
        Index("ix_item_workspace_id", "workspace_id"),
        Index("ix_item_node_id", "node_id"),
        Index("ix_item_type", "type"),
        Index("ix_item_status", "status"),
        Index("ix_item_assignee_id", "assignee_id"),
        Index("ix_item_due_date", "due_date"),
        {"comment": "条目表"},
    )

    def __str__(self) -> str:
        return self.title or f"条目#{self.id}"


class Notification(TimestampMixin, Base):
    """站内通知"""

    __tablename__ = "notification"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="CASCADE"), nullable=False, comment="接收人",
    )
    title: Mapped[str] = mapped_column(String(256), nullable=False, comment="标题")
    content: Mapped[Optional[str]] = mapped_column(Text, nullable=True, comment="通知内容")
    type: Mapped[str] = mapped_column(
        String(32), default="system", server_default="system", nullable=False,
        comment="类型 system / mention / task / …",
    )
    is_read: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default="0", nullable=False, comment="已读",
    )
    read_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, comment="阅读时间")
    source_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="来源类型")
    source_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="来源ID")
    sender_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="发送人",
    )

    # --- relationships ---
    user: Mapped["User"] = relationship(back_populates="notifications", foreign_keys=[user_id])
    sender: Mapped[Optional["User"]] = relationship(foreign_keys=[sender_id])

    __table_args__ = (
        Index("ix_notification_user_id", "user_id"),
        Index("ix_notification_is_read", "is_read"),
        Index("ix_notification_type", "type"),
        Index("ix_notification_created_at", "created_at"),
        {"comment": "通知表"},
    )

    def __str__(self) -> str:
        return self.title or f"通知#{self.id}"


class FileAsset(TimestampMixin, SoftDeleteMixin, Base):
    """文件/附件"""

    __tablename__ = "file_asset"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    workspace_id: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("workspace.id", ondelete="SET NULL"), nullable=True, comment="所属工作空间",
    )
    original_name: Mapped[str] = mapped_column(String(512), nullable=False, comment="原始文件名")
    storage_path: Mapped[str] = mapped_column(String(1024), nullable=False, comment="存储路径 / Object Key")
    file_size: Mapped[int] = mapped_column(BigInteger, default=0, nullable=False, comment="文件大小(bytes)")
    mime_type: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, comment="MIME 类型")
    file_hash: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, comment="文件哈希 (MD5/SHA256)")
    storage_type: Mapped[str] = mapped_column(
        String(16), default="local", server_default="local", nullable=False,
        comment="存储类型 local / s3 / oss / …",
    )
    target_type: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="关联资源类型")
    target_id: Mapped[Optional[str]] = mapped_column(String(64), nullable=True, comment="关联资源ID")
    uploaded_by: Mapped[Optional[int]] = mapped_column(
        BigInteger, ForeignKey("user.id", ondelete="SET NULL"), nullable=True, comment="上传人",
    )

    # --- relationships ---
    workspace: Mapped[Optional["Workspace"]] = relationship(back_populates="file_assets")
    uploader: Mapped[Optional["User"]] = relationship(foreign_keys=[uploaded_by])

    __table_args__ = (
        Index("ix_file_asset_workspace_id", "workspace_id"),
        Index("ix_file_asset_target", "target_type", "target_id"),
        Index("ix_file_asset_uploaded_by", "uploaded_by"),
        Index("ix_file_asset_file_hash", "file_hash"),
        {"comment": "文件资产表"},
    )

    def __str__(self) -> str:
        return self.original_name or f"文件#{self.id}"
