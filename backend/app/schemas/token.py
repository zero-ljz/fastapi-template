# app/schemas/token.py

from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    # sub (Subject) 是 JWT 的标准字段，通常用来存放用户 ID
    sub: str | None = None
