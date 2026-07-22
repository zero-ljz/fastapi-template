# tests/test_users.py

"""
用户模块测试
- 注册 / 登录 / 当前用户 / 修改密码 / 管理员操作
"""

from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings

# ===================================================================
# 注册
# ===================================================================


class TestRegister:
    """用户注册相关测试"""

    def test_register_success(self, client):
        """注册成功"""
        response = client.post(
            "/api/v1/users/register",
            json={
                "username": "newuser",
                "password": "Pass123456",
                "email": "new@example.com",
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == "newuser"
        assert data["email"] == "new@example.com"
        # 确保密码不会出现在响应中
        assert "password" not in data
        assert "hashed_password" not in data

    def test_register_duplicate_username(self, client):
        """重复用户名注册应返回 409"""
        payload = {
            "username": "dupuser",
            "password": "Pass123456",
            "email": "dup1@example.com",
        }
        resp1 = client.post("/api/v1/users/register", json=payload)
        assert resp1.status_code == 201

        # 相同用户名、不同邮箱
        payload["email"] = "dup2@example.com"
        resp2 = client.post("/api/v1/users/register", json=payload)
        assert resp2.status_code == 409

    def test_register_without_username(self, client):
        response = client.post(
            "/api/v1/users/register",
            json={"email": "email-only@example.com", "password": "Pass123456"},
        )
        assert response.status_code == 201
        assert response.json()["username"] is None

    def test_register_duplicate_email(self, client):
        """重复邮箱注册应返回 409"""
        payload1 = {
            "username": "emailuser1",
            "password": "Pass123456",
            "email": "same@example.com",
        }
        resp1 = client.post("/api/v1/users/register", json=payload1)
        assert resp1.status_code == 201

        # 不同用户名、相同邮箱
        payload2 = {
            "username": "emailuser2",
            "password": "Pass123456",
            "email": "same@example.com",
        }
        resp2 = client.post("/api/v1/users/register", json=payload2)
        assert resp2.status_code == 409


# ===================================================================
# 登录
# ===================================================================


class TestLogin:
    """登录相关测试"""

    def test_web_login_returns_no_refresh_token(self, client, test_user):
        """正确凭据登录成功"""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "testuser", "password": "Test123456"},
            headers={"X-Client-Type": "web"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["refresh_token"] is None
        assert data["expires_in"] > 0
        assert data["token_type"] == "bearer"

    def test_desktop_login_returns_refresh_token(self, client, test_user):
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "testuser", "password": "Test123456"},
            headers={"X-Client-Type": "desktop"},
        )

        assert response.status_code == 200
        assert response.json()["refresh_token"]

    def test_login_wrong_password(self, client, test_user):
        """密码错误应返回 401"""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "testuser", "password": "WrongPassword"},
        )
        assert response.status_code == 401

    def test_login_with_email(self, client, test_user):
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "test@example.com", "password": "Test123456"},
        )
        assert response.status_code == 200

    def test_login_nonexistent_user(self, client):
        """不存在的用户名应返回 401"""
        response = client.post(
            "/api/v1/login/access-token",
            data={"username": "nobody", "password": "Whatever123"},
        )
        assert response.status_code == 401


# ===================================================================
# 当前用户
# ===================================================================


class TestCurrentUser:
    """当前用户相关测试"""

    def test_get_current_user(self, client, auth_headers):
        """获取当前用户信息"""
        response = client.get("/api/v1/users/me", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "testuser"
        assert data["email"] == "test@example.com"

    def test_get_current_user_unauthorized(self, client):
        """未携带 Token 应返回 401"""
        response = client.get("/api/v1/users/me")
        assert response.status_code == 401

    def test_get_current_user_rejects_token_without_subject(self, client):
        token = jwt.encode(
            {
                "type": "access",
                "exp": datetime.now(UTC) + timedelta(minutes=5),
            },
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )
        response = client.get(
            "/api/v1/users/me", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 401
        assert response.json()["detail"] == "无效的 Token"

    def test_update_current_user(self, client, auth_headers):
        """更新当前用户昵称"""
        response = client.patch(
            "/api/v1/users/me",
            headers=auth_headers,
            json={"display_name": "Updated Name"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["display_name"] == "Updated Name"


# ===================================================================
# 修改密码
# ===================================================================


class TestPassword:
    """密码修改相关测试"""

    def test_update_password(self, client, auth_headers):
        """正确旧密码修改成功"""
        response = client.patch(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={"old_password": "Test123456", "new_password": "NewPass123"},
        )
        assert response.status_code == 200

    def test_update_password_wrong_old(self, client, auth_headers):
        """旧密码错误应返回 400"""
        response = client.patch(
            "/api/v1/users/me/password",
            headers=auth_headers,
            json={"old_password": "WrongOldPwd", "new_password": "NewPass123"},
        )
        assert response.status_code == 400


# ===================================================================
# 管理员操作
# ===================================================================


class TestAdminUsers:
    """管理员用户管理测试"""

    def test_admin_list_users(self, client, admin_auth_headers):
        """管理员获取用户列表"""
        response = client.get("/api/v1/users", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data

    def test_admin_list_users_forbidden(self, client, auth_headers):
        """普通用户获取用户列表应返回 403"""
        response = client.get("/api/v1/users", headers=auth_headers)
        assert response.status_code == 403

    def test_admin_get_user(self, client, admin_auth_headers, test_user):
        """管理员按 ID 查询用户"""
        user_id = test_user.id
        response = client.get(f"/api/v1/users/{user_id}", headers=admin_auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == user_id
        assert data["username"] == "testuser"

    def test_admin_delete_user(self, client, admin_auth_headers, db_session):
        """管理员删除用户"""
        from app.core.security import get_password_hash
        from app.models import User

        # 先创建一个待删除的用户，不删除管理员自己
        target_user = User(
            username="to_delete",
            email="delete@example.com",
            hashed_password=get_password_hash("Delete123456"),
            display_name="To Delete",
            is_active=True,
            is_superuser=False,
        )
        db_session.add(target_user)
        db_session.commit()
        db_session.refresh(target_user)
        target_id = target_user.id

        response = client.delete(
            f"/api/v1/users/{target_id}", headers=admin_auth_headers
        )
        assert response.status_code == 200


class TestRefreshSession:
    def test_refresh_rotates_token(self, client, test_user):
        login = client.post(
            "/api/v1/login/access-token",
            data={"username": "testuser", "password": "Test123456"},
            headers={"X-Client-Type": "desktop", "X-Device-Name": "Test PC"},
        )
        old_refresh_token = login.json()["refresh_token"]

        refreshed = client.post(
            "/api/v1/login/refresh",
            json={"refresh_token": old_refresh_token},
        )
        assert refreshed.status_code == 200
        assert refreshed.json()["refresh_token"] != old_refresh_token

        reused = client.post(
            "/api/v1/login/refresh",
            json={"refresh_token": old_refresh_token},
        )
        assert reused.status_code == 401

        new_token_after_reuse = client.post(
            "/api/v1/login/refresh",
            json={"refresh_token": refreshed.json()["refresh_token"]},
        )
        assert new_token_after_reuse.status_code == 401

    def test_logout_revokes_refresh_token(self, client, test_user):
        login = client.post(
            "/api/v1/login/access-token",
            data={"username": "testuser", "password": "Test123456"},
            headers={"X-Client-Type": "desktop"},
        )
        refresh_token = login.json()["refresh_token"]
        logout = client.post(
            "/api/v1/login/logout", json={"refresh_token": refresh_token}
        )
        assert logout.status_code == 200

        refreshed = client.post(
            "/api/v1/login/refresh", json={"refresh_token": refresh_token}
        )
        assert refreshed.status_code == 401

    def test_password_change_revokes_refresh_sessions(self, client, test_user):
        login = client.post(
            "/api/v1/login/access-token",
            data={"username": "testuser", "password": "Test123456"},
            headers={"X-Client-Type": "desktop"},
        )
        data = login.json()
        changed = client.patch(
            "/api/v1/users/me/password",
            headers={"Authorization": f"Bearer {data['access_token']}"},
            json={"old_password": "Test123456", "new_password": "NewPass123"},
        )
        assert changed.status_code == 200

        refreshed = client.post(
            "/api/v1/login/refresh", json={"refresh_token": data["refresh_token"]}
        )
        assert refreshed.status_code == 401
