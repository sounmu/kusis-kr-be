from datetime import datetime

from pydantic import BaseModel, Field


class RouteReqPostContent(BaseModel):
    title: str = Field(..., title="제목", description="제목을 입력해주세요")
    contents: str = Field(..., title="내용", description="내용을 입력해주세요")
    images: list[str] = Field([], title="이미지", description="이미지 URL을 입력해주세요")
    created_at: datetime = Field(datetime.now(), title="작성일", description="작성일을 입력해주세요")
    updated_at: datetime = Field(datetime.now(), title="수정일", description="수정일을 입력해주세요")
    is_deleted: bool = Field(False, title="삭제 여부", description="삭제 여부를 입력해주세요")
