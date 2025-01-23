from fastapi import APIRouter, status

from domain.schema.auth_schemas import (
    RouteReqAdminLogin,
    RouteReqUserRegister,
    RouteResAdminLogin,
    RouteResUserRegister,
)
from domain.service.auth_services import service_admin_login, service_user_register

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
async def admin_login(
    login_data: RouteReqAdminLogin
) -> RouteResAdminLogin:
    result = await service_admin_login(
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
async def user_register(
    request: RouteReqUserRegister
):
    result = await service_user_register(
        email=request.email,
        password=request.password,
        name=request.name
    )

    return result
