from fastapi import APIRouter, HTTPException, status
from firebase_admin import auth

from domain.schema.auth_schemas import RouteReqAdminLogin, RouteResAdminLogin
from domain.service.auth_services import service_admin_login

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

