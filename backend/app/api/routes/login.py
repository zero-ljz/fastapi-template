# app/api/routes/login.py

from fastapi import APIRouter, Request, Depends, UploadFile, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from typing import Annotated, Any
import datetime

from app import models
from app.api.deps import (
    SessionDep,
)
from app.core import security
from app.core.config import settings

from app.core.security import get_password_hash, verify_password

router = APIRouter()

@router.post("/login/access-token")
async def login_access_token(*, db: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    '''
    登录
    '''
    user = db.query(models.User).filter(models.User.username == form_data.username).first()
    if not user:
        raise HTTPException(status_code=400, detail="用户名不存在")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=400, detail="密码错误")

    access_token_expires = datetime.timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token":security.create_access_token(
            user.username, expires_delta=access_token_expires
        ),
        "token_type":"bearer",
    }

    