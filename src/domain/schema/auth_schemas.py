from datetime import datetime

from pydantic import BaseModel, EmailStr, Field


class RouteReqLoginAdmin(BaseModel):
    email: EmailStr = Field(title="email", description="관리자 이메일")
    password: str = Field(title="password", description="관리자 비밀번호")


class RouteResLoginAdmin(BaseModel):
    access_token: str = Field(title="access_token", description="액세스 토큰")
    refresh_token: str = Field(title="refresh_token", description="리프레시 토큰")
    token_type: str = Field("bearer", title="token_type", description="토큰 타입")


class RouteReqRegisterUser(BaseModel):
    email: EmailStr = Field(title="email", description="사용자 이메일")
    password: str = Field(title="password", description="사용자 비밀번호")
    name: str = Field(title="name", description="사용자 이름")


class RouteResRegisterUser(BaseModel):
    email: EmailStr = Field(title="email", description="사용자 이메일")
    name: str = Field(title="name", description="사용자 이름")


class RouteResGetUser(BaseModel):
    email: EmailStr = Field(title="email", description="사용자 이메일")
    name: str = Field(title="name", description="사용자 이름")
    created_at: datetime = Field(datetime.now(), title="created_at", description="사용자 생성일")
    updated_at: datetime = Field(datetime.now(), title="updated_at", description="사용자 최종 수정일")
    is_admin: bool = Field(False, title="is_admin", description="관리자: True, 사용자: False")
    is_active: bool = Field(True, title="is_active", description="활성: True, 비활성: False")
    is_deleted: bool = Field(False, title="is_deleted", description="삭제: True, 미삭제: False")


class RouteReqUpdateUser(BaseModel):
    name: str | None = Field(title="name", description="사용자 이름")
    is_admin: bool | None = Field(False, title="is_admin", description="관리자: True, 사용자: False")
    is_active: bool | None = Field(True, title="is_active", description="활성: True, 비활성: False")


class RouteResUpdateUser(BaseModel):
    email: EmailStr = Field(title="email", description="사용자 이메일")
    name: str = Field(title="name", description="사용자 이름")
    created_at: datetime = Field(datetime.now(), title="created_at", description="사용자 생성일")
    updated_at: datetime = Field(datetime.now(), title="updated_at", description="사용자 최종 수정일")
    is_admin: bool = Field(False, title="is_admin", description="관리자: True, 사용자: False")
    is_active: bool = Field(True, title="is_active", description="활성: True, 비활성: False")
    is_deleted: bool = Field(False, title="is_deleted", description="삭제: True, 미삭제: False")
