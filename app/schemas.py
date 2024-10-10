from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr


class UserCreate(UserBase):
    password: str
    username: str
    first_name: str
    last_name: str
    balance: int


class UserChangePassword(UserBase):
    password: str
    new_password: str
    confirm_new_password: str


class UserChangeName(UserBase):
    first_name: str
    last_name: str
    new_first_name: str
    new_last_name: str


class User(UserBase):
    id: int
    email: str
    first_name: str
    last_name: str
    balance: float
    created_at: datetime
    updated_at: datetime
    last_activity_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None


class UserAuth(BaseModel):
    username: str
    email: Optional[str] = None
    disabled: Optional[bool] = None


class UserInDB(UserAuth):
    hashed_password: str