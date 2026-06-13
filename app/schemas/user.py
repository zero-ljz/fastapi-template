import datetime
from pydantic import BaseModel

class UserBase(BaseModel):
    username: str
    nickname: str
    is_superuser: bool

class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    nickname: str | None = None
    password: str | None = None

class UserUpdateMe(BaseModel):
    nickname: str | None = None

class UpdatePassword(BaseModel):
    current_password: str
    new_password: str

class User(UserBase):
    id: int

    class Config:
        from_attributes = True

class UserOut(UserBase):
    id: int
    
    create_at: datetime.datetime
    update_at: datetime.datetime
    is_active: bool

class UsersOut(BaseModel):
    data: list[User]
    count: int