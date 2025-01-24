from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, status

from database import get_firestore_client
from dependency import get_current_active_admin
from domain.schema.content_schemas import RouteReqPostContent, RouteResGetContent, RouteResGetContentList
from domain.service.content_services import service_create_content, service_get_content, service_get_content_list

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
    response_model=RouteResGetContent,
    status_code=status.HTTP_200_OK,
)
async def create_content(
    content: RouteReqPostContent,
    current_user: Annotated[dict, Depends(get_current_active_admin)], # admin으로 변경하기.
    db = Depends(get_firestore_client),
) -> RouteResGetContent:
    response = await service_create_content(
        content=content,
        db=db,
    )
    return response
