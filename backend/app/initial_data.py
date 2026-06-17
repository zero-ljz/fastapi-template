#!/usr/bin/env python
# ruff: noqa: E402

"""初始化种子数据。

容器入口会在 Alembic 迁移后执行本脚本。脚本保持幂等：重复执行时只会补齐
缺失数据，不会重复插入同一批初始化记录。
"""

import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

ROOT_PATH = Path(__file__).resolve().parent.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(0, str(ROOT_PATH))

from app.core.config import settings
from app.core.db import SessionLocal
from app.core.logging import logger, setup_logging
from app.core.security import get_password_hash
from app.models import (
    User,
    Role,
    Permission,
    RolePermission,
    UserRole,
    Dictionary,
    SystemSetting,
    OperationLog,
    Notification,
    FileAsset,
    Workspace,
    WorkspaceUser,
    WorkspaceUserRole,
    Node,
    Item,
)
from app.services.user import get_user_by_username

DEMO_PASSWORD = "Demo123456"


def init_superuser() -> None:
    if not settings.FIRST_SUPERUSER or not settings.FIRST_SUPERUSER_PASSWORD:
        logger.info(
            "未配置 FIRST_SUPERUSER / FIRST_SUPERUSER_PASSWORD，跳过首个超级管理员初始化"
        )
        return

    with SessionLocal() as db:
        existing = get_user_by_username(db, settings.FIRST_SUPERUSER)
        if existing:
            logger.info(
                "超级管理员已存在，跳过初始化 | username={}", settings.FIRST_SUPERUSER
            )
            return

        user = User(
            username=settings.FIRST_SUPERUSER,
            email=settings.FIRST_SUPERUSER_EMAIL or None,
            password=get_password_hash(settings.FIRST_SUPERUSER_PASSWORD),
            nickname=settings.FIRST_SUPERUSER,
            is_active=True,
            is_superuser=True,
            status=1,
        )
        db.add(user)
        db.commit()
        logger.info("已创建首个超级管理员 | username={}", settings.FIRST_SUPERUSER)


def get_or_create_user(
    db: Session,
    *,
    username: str,
    email: str,
    nickname: str,
    is_superuser: bool = False,
) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if user:
        return user

    user = User(
        username=username,
        email=email,
        password=get_password_hash(DEMO_PASSWORD),
        nickname=nickname,
        is_active=True,
        is_superuser=is_superuser,
        status=1,
    )
    db.add(user)
    db.flush()
    return user


def get_seed_owner(db: Session) -> User:
    if settings.FIRST_SUPERUSER:
        superuser = get_user_by_username(db, settings.FIRST_SUPERUSER)
        if superuser:
            return superuser

    existing_superuser = db.scalar(
        select(User).where(User.is_superuser.is_(True)).order_by(User.id)
    )
    if existing_superuser:
        return existing_superuser

    return get_or_create_user(
        db,
        username="demo_manager",
        email="demo.manager@example.com",
        nickname="演示管理员",
    )


def get_or_create_role(
    db: Session,
    *,
    code: str,
    name: str,
    description: str,
    sort_order: int,
) -> Role:
    role = db.scalar(select(Role).where(Role.code == code))
    if role:
        return role

    role = Role(
        code=code,
        name=name,
        description=description,
        sort_order=sort_order,
        status=1,
    )
    db.add(role)
    db.flush()
    return role


def get_or_create_permission(
    db: Session,
    *,
    code: str,
    name: str,
    type_: str,
    parent: Permission | None = None,
    path: str | None = None,
    method: str | None = None,
    icon: str | None = None,
    sort_order: int = 0,
) -> Permission:
    permission = db.scalar(select(Permission).where(Permission.code == code))
    if permission:
        return permission

    permission = Permission(
        parent_id=parent.id if parent else None,
        code=code,
        name=name,
        type=type_,
        path=path,
        method=method,
        icon=icon,
        sort_order=sort_order,
        status=1,
    )
    db.add(permission)
    db.flush()
    return permission


def ensure_role_permission(db: Session, role: Role, permission: Permission) -> None:
    exists = db.scalar(
        select(RolePermission).where(
            RolePermission.role_id == role.id,
            RolePermission.permission_id == permission.id,
        )
    )
    if not exists:
        db.add(RolePermission(role_id=role.id, permission_id=permission.id))


def ensure_user_role(db: Session, user: User, role: Role) -> None:
    exists = db.scalar(
        select(UserRole).where(
            UserRole.user_id == user.id,
            UserRole.role_id == role.id,
        )
    )
    if not exists:
        db.add(UserRole(user_id=user.id, role_id=role.id))


def get_or_create_dictionary(
    db: Session,
    *,
    code: str,
    label: str,
    value: str | None = None,
    parent: Dictionary | None = None,
    sort_order: int = 0,
    remark: str | None = None,
) -> Dictionary:
    statement = select(Dictionary).where(
        Dictionary.code == code,
        Dictionary.value.is_(value) if value is None else Dictionary.value == value,
        Dictionary.parent_id.is_(None)
        if parent is None
        else Dictionary.parent_id == parent.id,
    )
    dictionary = db.scalar(statement)
    if dictionary:
        return dictionary

    dictionary = Dictionary(
        parent_id=parent.id if parent else None,
        code=code,
        label=label,
        value=value,
        sort_order=sort_order,
        status=1,
        remark=remark,
    )
    db.add(dictionary)
    db.flush()
    return dictionary


def get_or_create_system_setting(
    db: Session,
    *,
    key: str,
    value: str,
    description: str,
    is_public: bool,
) -> SystemSetting:
    setting = db.scalar(select(SystemSetting).where(SystemSetting.setting_key == key))
    if setting:
        return setting

    setting = SystemSetting(
        setting_key=key,
        setting_value=value,
        description=description,
        is_public=is_public,
    )
    db.add(setting)
    db.flush()
    return setting


def get_or_create_notification(
    db: Session,
    *,
    user: User,
    title: str,
    content: str,
    type_: str,
    sender: User | None = None,
    source_type: str | None = None,
    source_id: str | None = None,
) -> Notification:
    notification = db.scalar(
        select(Notification).where(
            Notification.user_id == user.id,
            Notification.title == title,
            Notification.source_type.is_(source_type)
            if source_type is None
            else Notification.source_type == source_type,
            Notification.source_id.is_(source_id)
            if source_id is None
            else Notification.source_id == source_id,
        )
    )
    if notification:
        return notification

    notification = Notification(
        user_id=user.id,
        title=title,
        content=content,
        type=type_,
        is_read=False,
        source_type=source_type,
        source_id=source_id,
        sender_id=sender.id if sender else None,
    )
    db.add(notification)
    db.flush()
    return notification


def get_or_create_file_asset(
    db: Session,
    *,
    workspace: Workspace,
    original_name: str,
    storage_path: str,
    uploader: User,
    target_type: str,
    target_id: str,
) -> FileAsset:
    asset = db.scalar(select(FileAsset).where(FileAsset.storage_path == storage_path))
    if asset:
        return asset

    asset = FileAsset(
        workspace_id=workspace.id,
        original_name=original_name,
        storage_path=storage_path,
        file_size=20480,
        mime_type="text/markdown",
        file_hash="seed-demo-roadmap-md",
        storage_type="local",
        target_type=target_type,
        target_id=target_id,
        uploaded_by=uploader.id,
    )
    db.add(asset)
    db.flush()
    return asset


def get_or_create_workspace(db: Session, *, owner: User) -> Workspace:
    workspace = db.scalar(select(Workspace).where(Workspace.code == "demo-workspace"))
    if workspace:
        return workspace

    workspace = Workspace(
        name="演示工作空间",
        code="demo-workspace",
        description="用于展示用户、权限、文件、任务和通知的初始化空间",
        logo_url="/static/logo.svg",
        owner_id=owner.id,
        status=1,
    )
    db.add(workspace)
    db.flush()
    return workspace


def ensure_workspace_user(
    db: Session,
    *,
    workspace: Workspace,
    user: User,
    role: WorkspaceUserRole,
) -> None:
    exists = db.scalar(
        select(WorkspaceUser).where(
            WorkspaceUser.workspace_id == workspace.id,
            WorkspaceUser.user_id == user.id,
        )
    )
    if not exists:
        db.add(
            WorkspaceUser(
                workspace_id=workspace.id,
                user_id=user.id,
                role=role.value,
            )
        )


def get_or_create_node(
    db: Session,
    *,
    workspace: Workspace,
    name: str,
    type_: str,
    creator: User,
    parent: Node | None = None,
    sort_order: int = 0,
    metadata_json: str | None = None,
) -> Node:
    node = db.scalar(
        select(Node).where(
            Node.workspace_id == workspace.id,
            Node.parent_id.is_(None) if parent is None else Node.parent_id == parent.id,
            Node.name == name,
            Node.type == type_,
        )
    )
    if node:
        return node

    node = Node(
        workspace_id=workspace.id,
        parent_id=parent.id if parent else None,
        name=name,
        type=type_,
        sort_order=sort_order,
        status=1,
        metadata_json=metadata_json,
        created_by=creator.id,
    )
    db.add(node)
    db.flush()
    return node


def get_or_create_item(
    db: Session,
    *,
    workspace: Workspace,
    node: Node,
    title: str,
    type_: str,
    creator: User,
    assignee: User | None,
    content: str,
    priority: int,
    status: str,
    metadata_json: str | None = None,
) -> Item:
    item = db.scalar(
        select(Item).where(
            Item.workspace_id == workspace.id,
            Item.node_id == node.id,
            Item.title == title,
        )
    )
    if item:
        return item

    item = Item(
        workspace_id=workspace.id,
        node_id=node.id,
        title=title,
        content=content,
        type=type_,
        priority=priority,
        status=status,
        assignee_id=assignee.id if assignee else None,
        metadata_json=metadata_json,
        created_by=creator.id,
    )
    db.add(item)
    db.flush()
    return item


def get_or_create_operation_log(
    db: Session,
    *,
    user: User,
    module: str,
    action: str,
    target_type: str,
    target_id: str,
    detail: str,
) -> OperationLog:
    log = db.scalar(
        select(OperationLog).where(
            OperationLog.user_id == user.id,
            OperationLog.module == module,
            OperationLog.action == action,
            OperationLog.target_type == target_type,
            OperationLog.target_id == target_id,
        )
    )
    if log:
        return log

    log = OperationLog(
        user_id=user.id,
        username=user.username,
        module=module,
        action=action,
        target_type=target_type,
        target_id=target_id,
        ip="127.0.0.1",
        user_agent="initial-data",
        request_method="SEED",
        request_url="/app/initial_data.py",
        request_body="{}",
        response_code=200,
        detail=detail,
        status=1,
    )
    db.add(log)
    db.flush()
    return log


def init_seed_data() -> None:
    with SessionLocal() as db:
        owner = get_seed_owner(db)
        member = get_or_create_user(
            db,
            username="demo_member",
            email="demo.member@example.com",
            nickname="演示成员",
        )
        viewer = get_or_create_user(
            db,
            username="demo_viewer",
            email="demo.viewer@example.com",
            nickname="演示观察者",
        )

        super_admin = get_or_create_role(
            db,
            code="super_admin",
            name="超级管理员",
            description="拥有系统全部管理权限",
            sort_order=1,
        )
        workspace_admin = get_or_create_role(
            db,
            code="workspace_admin",
            name="空间管理员",
            description="管理工作空间、成员和业务数据",
            sort_order=2,
        )
        project_member = get_or_create_role(
            db,
            code="project_member",
            name="项目成员",
            description="参与任务处理和文件协作",
            sort_order=3,
        )
        readonly_viewer = get_or_create_role(
            db,
            code="readonly_viewer",
            name="只读观察者",
            description="只能查看公开业务数据",
            sort_order=4,
        )

        system_menu = get_or_create_permission(
            db,
            code="system:menu",
            name="系统管理",
            type_="menu",
            path="/system",
            icon="settings",
            sort_order=10,
        )
        user_permission = get_or_create_permission(
            db,
            code="system:user:manage",
            name="用户管理",
            type_="api",
            parent=system_menu,
            path="/api/v1/users",
            method="GET",
            sort_order=11,
        )
        role_permission = get_or_create_permission(
            db,
            code="system:role:manage",
            name="角色权限管理",
            type_="api",
            parent=system_menu,
            path="/admin/role",
            method="GET",
            sort_order=12,
        )
        workspace_menu = get_or_create_permission(
            db,
            code="workspace:menu",
            name="工作空间",
            type_="menu",
            path="/workspace",
            icon="briefcase",
            sort_order=20,
        )
        workspace_manage = get_or_create_permission(
            db,
            code="workspace:manage",
            name="空间管理",
            type_="api",
            parent=workspace_menu,
            path="/api/v1/workspaces",
            method="GET",
            sort_order=21,
        )
        item_manage = get_or_create_permission(
            db,
            code="item:manage",
            name="条目管理",
            type_="api",
            parent=workspace_menu,
            path="/api/v1/items",
            method="GET",
            sort_order=22,
        )
        notification_read = get_or_create_permission(
            db,
            code="system:notification:read",
            name="通知查看",
            type_="api",
            parent=system_menu,
            path="/api/v1/notifications",
            method="GET",
            sort_order=13,
        )

        permissions = [
            system_menu,
            user_permission,
            role_permission,
            notification_read,
            workspace_menu,
            workspace_manage,
            item_manage,
        ]
        for permission in permissions:
            ensure_role_permission(db, super_admin, permission)
        for permission in [
            notification_read,
            workspace_menu,
            workspace_manage,
            item_manage,
        ]:
            ensure_role_permission(db, workspace_admin, permission)
        for permission in [workspace_menu, item_manage, notification_read]:
            ensure_role_permission(db, project_member, permission)
        for permission in [workspace_menu, notification_read]:
            ensure_role_permission(db, readonly_viewer, permission)

        if owner.is_superuser:
            ensure_user_role(db, owner, super_admin)
        ensure_user_role(db, owner, workspace_admin)
        ensure_user_role(db, member, project_member)
        ensure_user_role(db, viewer, readonly_viewer)

        notification_type = get_or_create_dictionary(
            db, code="notification_type", label="通知类型", sort_order=10
        )
        get_or_create_dictionary(
            db,
            code="notification_type",
            label="系统通知",
            value="system",
            parent=notification_type,
            sort_order=1,
        )
        get_or_create_dictionary(
            db,
            code="notification_type",
            label="任务通知",
            value="task",
            parent=notification_type,
            sort_order=2,
        )
        storage_type = get_or_create_dictionary(
            db, code="storage_type", label="存储类型", sort_order=20
        )
        get_or_create_dictionary(
            db,
            code="storage_type",
            label="本地存储",
            value="local",
            parent=storage_type,
            sort_order=1,
        )

        node_type = get_or_create_dictionary(
            db, code="node_type", label="节点类型", sort_order=30
        )
        get_or_create_dictionary(
            db,
            code="node_type",
            label="项目阶段",
            value="phase",
            parent=node_type,
            sort_order=1,
        )
        get_or_create_dictionary(
            db,
            code="node_type",
            label="文档目录",
            value="folder",
            parent=node_type,
            sort_order=2,
        )
        item_type = get_or_create_dictionary(
            db, code="item_type", label="条目类型", sort_order=40
        )
        get_or_create_dictionary(
            db,
            code="item_type",
            label="任务",
            value="task",
            parent=item_type,
            sort_order=1,
        )
        get_or_create_dictionary(
            db,
            code="item_type",
            label="文档",
            value="doc",
            parent=item_type,
            sort_order=2,
        )
        item_status = get_or_create_dictionary(
            db, code="item_status", label="条目状态", sort_order=50
        )
        get_or_create_dictionary(
            db,
            code="item_status",
            label="待处理",
            value="open",
            parent=item_status,
            sort_order=1,
        )
        get_or_create_dictionary(
            db,
            code="item_status",
            label="进行中",
            value="in_progress",
            parent=item_status,
            sort_order=2,
        )
        get_or_create_dictionary(
            db,
            code="item_status",
            label="已完成",
            value="done",
            parent=item_status,
            sort_order=3,
        )
        priority = get_or_create_dictionary(
            db, code="priority", label="优先级", sort_order=60
        )
        get_or_create_dictionary(
            db, code="priority", label="中", value="2", parent=priority, sort_order=2
        )
        get_or_create_dictionary(
            db, code="priority", label="高", value="3", parent=priority, sort_order=3
        )

        get_or_create_system_setting(
            db,
            key="site.name",
            value=settings.PROJECT_NAME,
            description="前台显示的站点名称",
            is_public=True,
        )
        get_or_create_system_setting(
            db,
            key="workspace.default_role",
            value=WorkspaceUserRole.MEMBER.value,
            description="新成员加入工作空间时的默认角色",
            is_public=False,
        )
        get_or_create_system_setting(
            db,
            key="upload.max_size_mb",
            value="20",
            description="演示环境默认上传大小限制",
            is_public=True,
        )

        workspace = get_or_create_workspace(db, owner=owner)
        ensure_workspace_user(
            db, workspace=workspace, user=owner, role=WorkspaceUserRole.OWNER
        )
        ensure_workspace_user(
            db, workspace=workspace, user=member, role=WorkspaceUserRole.MEMBER
        )
        ensure_workspace_user(
            db, workspace=workspace, user=viewer, role=WorkspaceUserRole.VIEWER
        )

        planning = get_or_create_node(
            db,
            workspace=workspace,
            name="产品规划",
            type_="phase",
            creator=owner,
            sort_order=1,
            metadata_json='{"color":"#2563eb"}',
        )
        documents = get_or_create_node(
            db,
            workspace=workspace,
            name="项目文档",
            type_="folder",
            creator=owner,
            parent=planning,
            sort_order=2,
            metadata_json='{"icon":"folder"}',
        )

        roadmap = get_or_create_item(
            db,
            workspace=workspace,
            node=planning,
            title="梳理第一版产品路线图",
            type_="task",
            creator=owner,
            assignee=member,
            content="明确核心用户、关键功能和第一阶段交付范围。",
            priority=3,
            status="in_progress",
            metadata_json='{"estimate":"3d","tags":["planning","demo"]}',
        )
        handbook = get_or_create_item(
            db,
            workspace=workspace,
            node=documents,
            title="维护项目协作文档",
            type_="doc",
            creator=owner,
            assignee=member,
            content="记录需求、接口、会议纪要和发布说明。",
            priority=2,
            status="open",
            metadata_json='{"template":"knowledge-base"}',
        )

        get_or_create_notification(
            db,
            user=member,
            title="你被分配了路线图任务",
            content="请完善第一版产品路线图，并在完成后更新任务状态。",
            type_="task",
            sender=owner,
            source_type="item",
            source_id=str(roadmap.id),
        )
        get_or_create_notification(
            db,
            user=viewer,
            title="欢迎加入演示工作空间",
            content="你当前拥有只读权限，可以查看空间内公开的任务和文档。",
            type_="system",
            sender=owner,
            source_type="workspace",
            source_id=str(workspace.id),
        )

        asset = get_or_create_file_asset(
            db,
            workspace=workspace,
            original_name="product-roadmap.md",
            storage_path="/uploads/demo/product-roadmap.md",
            uploader=owner,
            target_type="item",
            target_id=str(roadmap.id),
        )

        get_or_create_operation_log(
            db,
            user=owner,
            module="initial_data",
            action="seed",
            target_type="workspace",
            target_id=str(workspace.id),
            detail=f"初始化演示工作空间和文件 {asset.original_name}",
        )
        get_or_create_operation_log(
            db,
            user=owner,
            module="initial_data",
            action="seed",
            target_type="item",
            target_id=str(handbook.id),
            detail="初始化项目协作文档条目",
        )

        db.commit()
        logger.info(
            "初始化种子数据完成 | workspace={} | demo_password={}",
            workspace.code,
            DEMO_PASSWORD,
        )


def main() -> None:
    setup_logging()
    init_superuser()
    init_seed_data()


if __name__ == "__main__":
    main()
