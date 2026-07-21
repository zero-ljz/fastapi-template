# app/schemas/token.py

from pydantic import BaseModel, Field


class Token(BaseModel):
    access_token: str
    refresh_token: str | None = None
    token_type: str = "bearer"
    expires_in: int


class TokenPayload(BaseModel):
    sub: str | None = None
    type: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32)
    client_type: str | None = Field(None, max_length=32)
    device_name: str | None = Field(None, max_length=128)


class RevokeTokenRequest(BaseModel):
    refresh_token: str = Field(..., min_length=32)
