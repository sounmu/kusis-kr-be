from typing import Annotated

from fastapi import APIRouter, Depends, status

from dependency import get_async_firestore_client, get_current_active_admin
from domain.schema.auth_schemas import (
    RouteReqLoginAdmin,
    RouteReqRegisterUser,
    RouteReqUpdateUser,
    RouteResGetUser,
    RouteResLoginAdmin,
    RouteResRegisterUser,
    RouteResUpdateUser,
)
from domain.service.auth_services import (
    service_delete_user,
    service_get_user,
    service_login_admin,
    service_register_user,
    service_update_user,
)

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post(
    "/admin/login",
    summary="관리자 로그인",
    description="관리자 로그인",
    response_model=RouteResLoginAdmin,
    status_code=status.HTTP_200_OK,
)
async def login_admin(
    login_data: RouteReqLoginAdmin
) -> RouteResLoginAdmin:
    result = await service_login_admin(
        email=login_data.email,
        password=login_data.password
    )

    return result


@router.post(
    "/user/register",
    summary="사용자 회원가입",
    description="사용자 회원가입",
    response_model=RouteResRegisterUser,
    status_code=status.HTTP_200_OK,
)
async def register_user(
    request: RouteReqRegisterUser
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
    db = Depends(get_async_firestore_client),
):
    result = await service_get_user(
        uid=uid,
        db=db
    )

    return result


@router.put(
    "/admin/{uid}",
    summary="사용자 정보 수정",
    description="""사용자 정보 수정""",
    response_model=RouteResUpdateUser,
    status_code=status.HTTP_200_OK,
)
async def update_admin(
    uid: str,
    request: RouteReqUpdateUser,
    current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_async_firestore_client),
) -> RouteResUpdateUser:
    result = await service_update_user(
        uid=uid,
        request=request,
        db=db
    )

    return result


@router.delete(
    "/admin/{uid}",
    summary="사용자 삭제",
    description="""사용자 삭제""",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_admin(
    uid: str,
    current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_async_firestore_client),
) -> None:
    await service_delete_user(
        uid=uid,
        db=db
    )

    return
