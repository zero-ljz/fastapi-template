# app/api/deps.py
from collections.abc import Generator, AsyncGenerator
from typing import Annotated
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from app.core.db import SessionLocal, AsyncSessionLocal


def get_session() -> Generator[Session, None, None]:
    with SessionLocal() as session:
        yield session


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]
AsyncSessionDep = Annotated[AsyncSession, Depends(get_async_session)]
