from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Path, status

from database import db
from dependency import get_current_active_user
from domain.schema.content_schema import RouteResGetContent, RouteResGetContentList
from domain.service.content_service import service_get_content

router = APIRouter(
    prefix="/content",
    tags=["content"]
)

@router.get(
    """
    게시글 ID로 조회합니다.

    Args:
        content_id (int): 게시글 ID (양수)
        db: 데이터베이스 종속성
        current_user: 현재 활성 사용자 종속성

    Returns:
        RouteResGetContentList: 게시글 조회 결과
    """
    "/{content_id}",
    summary="게시글 조회",
    description="""게시글을 ID로 조회합니다.""",
    response_model=RouteResGetContent,
    status_code=status.HTTP_200_OK,
)
async def get_content(
    content_id: Annotated[int, Path(description="게시글 ID", gt=0)],
    db=Depends(db),
) -> RouteResGetContent:
    response = service_get_content(
        content_id=content_id,
        db=db,
    )

    return response

@router.post(
    "/",
    summary="게시글 작성",
    status_code=status.HTTP_200_OK,
)
async def create_content():
    pass
