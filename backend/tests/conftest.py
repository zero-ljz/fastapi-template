# tests/conftest.py

"""
测试基础设施
- 使用 SQLite 内存数据库，每个测试函数独立建表/销毁
- 提供 TestClient、预置用户、认证 headers 等 fixtures
"""

import pytest
from sqlalchemy import create_engine, event, BigInteger
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from fastapi.testclient import TestClient

from app.models import Base, User
from app.core.security import get_password_hash
from app.api.deps import get_session
from app.main import app


# ---------------------------------------------------------------------------
# SQLite 兼容性：BigInteger → INTEGER（使 autoincrement 正常工作）
# SQLite 仅对 "INTEGER" 类型的主键支持自增，BigInteger 会渲染为 BIGINT
# ---------------------------------------------------------------------------


@compiles(BigInteger, "sqlite")
def compile_big_integer_sqlite(type_, compiler, **kw):
    return "INTEGER"


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="function")
def db_session():
    """
    每个测试函数独立的数据库会话。
    使用 StaticPool 确保 SQLite 内存数据库在所有连接间共享。
    测试前建表，测试后销毁，确保用例之间完全隔离。
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )

    # SQLite 需要启用外键约束
    @event.listens_for(engine, "connect")
    def set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    Base.metadata.create_all(bind=engine)
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI TestClient，自动将 get_session 依赖替换为测试数据库会话。
    """

    def override_get_session():
        yield db_session

    app.dependency_overrides[get_session] = override_get_session

    with TestClient(app, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db_session):
    """创建普通测试用户"""
    user = User(
        username="testuser",
        password=get_password_hash("Test123456"),
        email="test@example.com",
        nickname="Test User",
        is_active=True,
        is_superuser=False,
        status=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_superuser(db_session):
    """创建超级管理员测试用户"""
    user = User(
        username="admin",
        password=get_password_hash("Admin123456"),
        email="admin@example.com",
        nickname="Admin",
        is_active=True,
        is_superuser=True,
        status=1,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture(scope="function")
def auth_headers(client, test_user):
    """普通用户的认证 headers"""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "testuser", "password": "Test123456"},
    )
    assert response.status_code == 200, f"登录失败: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def admin_auth_headers(client, test_superuser):
    """管理员的认证 headers"""
    response = client.post(
        "/api/v1/login/access-token",
        data={"username": "admin", "password": "Admin123456"},
    )
    assert response.status_code == 200, f"管理员登录失败: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
