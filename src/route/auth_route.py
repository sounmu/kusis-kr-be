from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependency import get_current_active_admin, get_firestore_client
from domain.schema.auth_schemas import (
    RouteReqAdminLogin,
    RouteReqUserRegister,
    RouteResAdminLogin,
    RouteResGetUser,
    RouteResUserRegister,
)
from domain.service.auth_services import service_get_user, service_login_admin, service_register_user

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/admin/login",
    summary="관리자 로그인",
    description="관리자 로그인",
    response_model=RouteResAdminLogin,
    status_code=status.HTTP_200_OK,
)
async def login_admin(
    login_data: RouteReqAdminLogin
) -> RouteResAdminLogin:
    result = await service_login_admin(
        email=login_data.email,
        password=login_data.password
    )

    return result


@router.post(
    "/user/register",
    summary="사용자 회원가입",
    description="사용자 회원가입",
    response_model=RouteResUserRegister,
    status_code=status.HTTP_200_OK,
)
async def register_user(
    request: RouteReqUserRegister
):
    result = await service_register_user(
        email=request.email,
        password=request.password,
        name=request.name
    )

    return result


@router.get(
    "/admin/{uid}",
    summary="사용자 정보 조회",
    description="""사용자 정보 조회""",
    response_model=RouteResGetUser,
    status_code=status.HTTP_200_OK,
)
async def get_admin(
    uid: str,
    current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_firestore_client),
):
    result = await service_get_user(
        uid=uid,
        db=db
    )

    return result

