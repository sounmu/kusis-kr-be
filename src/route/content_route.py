from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from database import get_firestore_client
from dependency import get_current_active_user
from domain.schema.content_schemas import RouteResGetContent, RouteResGetContentList
from domain.service.content_services import service_get_content

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


@router.post(
    "/admin/create",
    summary="게시글 작성",
    status_code=status.HTTP_200_OK,
)
async def create_content():
    pass
