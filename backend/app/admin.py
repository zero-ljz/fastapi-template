# app/admin.py

"""仅管理核心用户与刷新会话的 SQLAdmin 后台。"""

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from sqlalchemy import or_, select
from sqladmin import Admin, ModelView
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request

from app.core.config import settings
from app.core.db import SessionLocal, engine
from app.core.security import verify_password
from app.models import RefreshSession, User


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        identifier = str(form.get("username", ""))
        password = str(form.get("password", ""))
        with SessionLocal() as db:
            user = db.scalar(
                select(User).where(
                    or_(
                        User.email == identifier.lower(),
                        User.username == identifier,
                    )
                )
            )
            if not user or not user.is_active or not user.is_superuser:
                return False
            valid, _ = verify_password(password, user.hashed_password)
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
        User.email,
        User.username,
        User.display_name,
        User.is_active,
        User.is_superuser,
        User.last_login_at,
        User.created_at,
    ]
    column_searchable_list = [User.email, User.username, User.display_name]
    column_sortable_list = [User.id, User.email, User.created_at]
    column_details_exclude_list = [User.hashed_password, User.refresh_sessions]
    form_excluded_columns = [
        User.hashed_password,
        User.refresh_sessions,
        User.created_at,
        User.updated_at,
    ]


class RefreshSessionAdmin(ModelView, model=RefreshSession):
    name = "登录会话"
    name_plural = "登录会话"
    icon = "fa-solid fa-laptop"
    can_create = False
    can_edit = False
    can_delete = False
    column_list = [
        RefreshSession.id,
        RefreshSession.user,
        RefreshSession.client_type,
        RefreshSession.device_name,
        RefreshSession.ip_address,
        RefreshSession.expires_at,
        RefreshSession.revoked_at,
        RefreshSession.created_at,
    ]
    column_searchable_list = [
        RefreshSession.client_type,
        RefreshSession.device_name,
        RefreshSession.ip_address,
    ]
    column_sortable_list = [RefreshSession.id, RefreshSession.expires_at]
    column_details_exclude_list = [RefreshSession.token_hash]


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
    admin.add_view(UserAdmin)
    admin.add_view(RefreshSessionAdmin)
    return admin
