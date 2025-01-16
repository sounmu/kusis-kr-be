from typing import Annotated

from fastapi import APIRouter, Depends, Path, HTTPException, status
from database import db

from dependency import get_current_active_user
from domain.service.content_service import service_get_content
from domain.schema.content_schema import RouteResGetContentList

router = APIRouter(
    prefix="/content",
    tags=["content"]
)

@router.get(
    "/{content_id}",
    summary="게시글 전체 조회",
    description="""게시글 전체를 리스트 형태로 조회합니다.""",
    response_model=RouteResGetContentList,
    status_code=status.HTTP_200_OK,
)
async def get_content(
    content_id: Annotated[int, Path(description="게시글 ID", gt=0)],
    db=Depends(db),
    current_user=Depends(get_current_active_user)
) -> RouteResGetContentList:
    content = service_get_content(content_id, db)
    return content

@router.post(
    "/",
    summary="게시글 작성",
    status_code=status.HTTP_200_OK,
)
async def create_content():
    pass
