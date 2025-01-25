from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from database import get_firestore_client
from dependency import get_current_active_admin
from domain.schema.content_schemas import (
    RouteReqPostContent,
    RouteReqPutContent,
    RouteResGetContent,
    RouteResGetContentDetail,
    RouteResGetContentList,
)
from domain.service.content_services import (
    service_create_content,
    service_delete_content,
    service_get_content,
    service_get_content_detail,
    service_get_content_list,
    service_update_content,
)

router = APIRouter(
    prefix="/content",
    tags=["content"]
)


@router.get(
    "/{post_number}",
    summary="게시글 조회",
    description="""게시글을 Post Number로 조회합니다.""",
    response_model=RouteResGetContent,
    status_code=status.HTTP_200_OK,
)
async def get_content(
    post_number: Annotated[int, Path(description="게시글 Post Number", gt=0)],
    db = Depends(get_firestore_client),
) -> RouteResGetContent:
    response = await service_get_content(
        post_number=post_number,
        db=db,
    )

    return response


@router.get(
    "",
    summary="게시글 목록 조회",
    description="""게시글 목록을 조회합니다.""",
    response_model=RouteResGetContentList,
    status_code=status.HTTP_200_OK,
)
async def get_content_list(
    page: Annotated[
        int, Query(description="페이지 번호", example=1,gt=0)
    ] = 1,
    limit: Annotated[
        int, Query(description="페이지 당 게시글 수", example=10,gt=0)
    ] = 10,
    db = Depends(get_firestore_client),
) -> RouteResGetContentList:
    response = await service_get_content_list(
        page=page,
        limit=limit,
        db=db,
    )
    return response


@router.post(
    "/admin/create",
    summary="게시글 작성",
    description="""게시글을 작성합니다.""",
    response_model=RouteResGetContent,
    status_code=status.HTTP_200_OK,
)
async def create_content(
    content: RouteReqPostContent,
    current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_firestore_client),
) -> RouteResGetContent:
    response = await service_create_content(
        content=content,
        db=db,
    )
    return response


@router.put(
    "/admin/{post_number}",
    summary="게시글 수정",
    description="""게시글을 수정합니다.""",
    response_model=RouteResGetContent,
    status_code=status.HTTP_200_OK,
)
async def update_content(
    post_number: Annotated[int, Path(description="게시글 Post Number", gt=0)],
    request: RouteReqPutContent,
    current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_firestore_client),
) -> RouteResGetContent:
    response = await service_update_content(
        post_number=post_number,
        request=request,
        db=db,
    )
    return response


@router.delete(
    "/admin/{post_number}",
    summary="게시글 삭제",
    description="""게시글을 삭제합니다.""",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_content(
    post_number: Annotated[int, Path(description="게시글 Post Number", gt=0)],
    current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_firestore_client),
) -> None:
    await service_delete_content(
        post_number=post_number,
        db=db,
    )
    return


@router.get(
    "/admin/{post_number}",
    summary="게시글 상세 조회",
    description="""게시글을 Post Number로 상세 조회합니다.""",
    response_model=RouteResGetContentDetail,
    status_code=status.HTTP_200_OK,
)
async def get_content_detail(
    post_number: Annotated[int, Path(description="게시글 Post Number", gt=0)],
    current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_firestore_client),
) -> RouteResGetContentDetail:
    response = await service_get_content_detail(
        post_number=post_number,
        db=db,
    )

    return response
