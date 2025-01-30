from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, Path, Query, UploadFile, status

from database import get_async_firestore_client
from dependency import get_image_uploader
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
from utils.image_utils import ImageUploader

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
    db = Depends(get_async_firestore_client),
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
        int, Query(description="페이지 번호", example=1, gt=0)
    ] = 1,
    limit: Annotated[
        int, Query(description="페이지 당 게시글 수", example=10, gt=0)
    ] = 10,
    category: Annotated[
        str | None, Query(regex="^(apply|notice|cardnews)$")
    ] = None,
    db = Depends(get_async_firestore_client),
) -> RouteResGetContentList:
    response = await service_get_content_list(
        page=page,
        limit=limit,
        category=category,
        db=db,
    )
    return response


@router.post(
    "/admin/create",
    summary="게시글 작성",
    description="""게시글을 작성합니다. 이미지 파일도 함께 업로드할 수 있습니다.""",
    response_model=RouteResGetContent,
    status_code=status.HTTP_201_CREATED,
)
async def create_content(
    category: Annotated[str, Form()],
    title: Annotated[str, Form()],
    contents: Annotated[str, Form()],
    image_uploader: Annotated[ImageUploader, Depends(get_image_uploader)],
    images: list[UploadFile] = File(None),
    db = Depends(get_async_firestore_client),
) -> RouteResGetContent:
    content = RouteReqPostContent(
        category=category,
        title=title,
        contents=contents
    )
    response = await service_create_content(
        content=content,
        images=images,
        db=db,
        image_uploader=image_uploader,
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
    #current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_async_firestore_client),
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
    #current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_async_firestore_client),
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
    #current_user: Annotated[dict, Depends(get_current_active_admin)],
    db = Depends(get_async_firestore_client),
) -> RouteResGetContentDetail:
    response = await service_get_content_detail(
        post_number=post_number,
        db=db,
    )
    return response
