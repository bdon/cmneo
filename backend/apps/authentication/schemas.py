from ninja import Schema
from datetime import datetime
from typing import Optional


class RegisterSchema(Schema):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class LoginSchema(Schema):
    email: str
    password: str


class MagicLinkRequestSchema(Schema):
    email: str


class MagicLinkVerifySchema(Schema):
    token: str


class UserSchema(Schema):
    id: int
    email: str
    first_name: str
    last_name: str
    is_active: bool
    date_joined: datetime


class TokenSchema(Schema):
    access_token: str
    token_type: str = "bearer"
    user: UserSchema


class MessageSchema(Schema):
    message: str
