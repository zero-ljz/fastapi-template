import os, datetime
from sqlalchemy import Integer, Float, Numeric, String, Text, Unicode, Boolean, DateTime, Date, Time
from sqlalchemy import Table, Column, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

class BaseMixin:
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=datetime.datetime.now(datetime.timezone.utc), onupdate=datetime.datetime.now(datetime.timezone.utc))
    is_active = Column(Boolean, default=True)

# 系统字典
class Option(Base, BaseMixin):
    __tablename__ = 'option'
    name = Column(String(255), nullable=False, comment="名称")
    value = Column(String(255), nullable=False, comment="值")

    def __str__(self):
        return self.name

# 用户
class User(Base, BaseMixin):
    __tablename__ = 'user'
    username = Column(String(255), nullable=False, comment="用户名")
    password = Column(String(255), nullable=False, comment="密码")
    is_superuser = Column(Boolean, unique=False, default=False, comment="是否为超级用户")
    nickname = Column(String(255), nullable=False, comment="昵称")

    projects = relationship('Project', backref="user")

    authorize_projects = relationship("Project", secondary="project_user_authorize", back_populates="authorize_users")

    def __str__(self):
        return self.username
    
# 14个
# Dictionary, System_Config, Permission, 
# User, Workspace, Role, 
# Role_Permission, User_Role, Workspace_User, 
# Notification, Operation_Log, Node, Item
# FileAsset

# 按模块划分
# Auth & RBAC: User, Role, Permission, RolePermission, UserRole
# System: Dictionary, SystemConfig, OperationLog
# Workspace: Workspace, WorkspaceUser
# Business: Node, Item, Notification, FileAsset