# tests/conftest.py

"""
测试基础设施
- 使用临时 SQLite 文件共享同步测试夹具与异步 API 会话
- API 通过 aiosqlite + AsyncSession 执行真实异步数据库调用
- 每个测试函数独立建表/销毁
"""

import asyncio

import pytest
from sqlalchemy import BigInteger, create_engine, event
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from fastapi.testclient import TestClient

from app.models import Base, User
from app.core.security import get_password_hash
from app.api.deps import get_async_session
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


def enable_sqlite_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()


@pytest.fixture(scope="function")
def db_engine(tmp_path):
    database_path = tmp_path / "test.db"
    engine = create_engine(
        f"sqlite:///{database_path.as_posix()}",
        connect_args={"check_same_thread": False},
        echo=False,
    )
    event.listen(engine, "connect", enable_sqlite_foreign_keys)
    Base.metadata.create_all(bind=engine)
    try:
        yield engine, database_path
    finally:
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


@pytest.fixture(scope="function")
def db_session(db_engine):
    engine, _ = db_engine
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_engine):
    """将 AsyncSession 依赖替换为基于 aiosqlite 的测试会话。"""
    _, database_path = db_engine
    async_engine = create_async_engine(
        f"sqlite+aiosqlite:///{database_path.as_posix()}",
        echo=False,
    )
    event.listen(async_engine.sync_engine, "connect", enable_sqlite_foreign_keys)
    TestAsyncSessionLocal = async_sessionmaker(
        bind=async_engine,
        autoflush=False,
        expire_on_commit=False,
    )

    async def override_get_async_session():
        async with TestAsyncSessionLocal() as session:
            yield session

    app.dependency_overrides[get_async_session] = override_get_async_session

    with TestClient(app, base_url="http://test") as c:
        yield c

    app.dependency_overrides.clear()
    asyncio.run(async_engine.dispose())


@pytest.fixture(scope="function")
def test_user(db_session):
    """创建普通测试用户"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("Test123456"),
        display_name="Test User",
        is_active=True,
        is_superuser=False,
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
        email="admin@example.com",
        hashed_password=get_password_hash("Admin123456"),
        display_name="Admin",
        is_active=True,
        is_superuser=True,
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
