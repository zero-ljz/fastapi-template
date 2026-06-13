from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import insert, delete, update, select, func, text, and_, or_, not_, desc, asc

from app.api.deps import (
    SessionDep,
    CurrentUser,
    get_current_active_superuser,
)

from app.models import User
import app.api.schemas.users as schemas
from app.core.security import get_password_hash, verify_password

router = APIRouter()

@router.get("/", response_model=schemas.UsersOut)
def read_users(
    *,
    db: SessionDep,
    current_user: CurrentUser,
    page: int = 1,
    per_page: int = 10,
    captain_id: int | None = None,
) -> Any:

    count = db.execute(select(func.count()).select_from(User)).where(User.c.id > 1).scalar()
    
    stmt = (
        select(User.c.id, User.c.username)
        .select_from(User)
        .where(User.c.id > 1)
        .order_by(desc(User.c.id)) 
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    users = db.execute(stmt).scalars().all()






# ORM
db.query(User).all()