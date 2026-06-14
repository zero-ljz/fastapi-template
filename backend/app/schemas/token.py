# app/schemas/token.py

from pydantic import BaseModel, Field

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    # sub (Subject) 是 JWT 的标准字段，通常用来存放用户 ID
    # 显式声明为 str 或 int（取决于你的用户主键类型）
    sub: str | None = None
    
    # 如果你在生成 JWT 时放入了其他字段，也可以在这里定义
    # exp: int | None = None