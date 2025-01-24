from datetime import datetime

from pydantic import BaseModel, Field


class RouteReqPostContent(BaseModel):
    title: str = Field(title="title", description="게시글 제목")
    contents: str = Field(title="contents", description="게시글 내용")
    images: list[str] = Field([], title="images", description="이미지 URL 모음")


class DomainReqPostContent(BaseModel):
    post_number: int = Field(title="post_number", description="게시글 Post Number")
    title: str = Field(title="title", description="게시글 제목")
    contents: str = Field(title="contents", description="게시글 내용")
    images: list[str] = Field([], title="images", description="이미지 URL 모음")
    created_at: datetime = Field(datetime.now(), title="created_at", description="게시글 작성일")
    updated_at: datetime = Field(datetime.now(), title="updated_at", description="게시글 최종 수정일")
    is_deleted: bool = Field(False, title="is_deleted", description="삭제: True, 미삭제: False")


class RouteResGetContent(BaseModel):
    content_id: str = Field(title="content_id", description="게시글 ID")
    post_number: int = Field(title="post_number", description="게시글 Post Number")
    title: str = Field(title="title", description="게시글 제목")
    contents: str = Field(title="contents", description="게시글 내용")
    images: list[str] = Field([], title="images", description="이미지 URL 모음")
    created_at: datetime = Field(datetime.now(), title="created_at", description="게시글 작성일")
    updated_at: datetime = Field(datetime.now(), title="updated_at", description="게시글 최종 수정일")
    is_deleted: bool = Field(False, title="is_deleted", description="삭제: True, 미삭제: False")


class RouteResContentSummary(BaseModel):
    content_id: str = Field(title="content_id", description="게시글 ID")
    title: str = Field(title="title", description="게시글 제목")
    first_image: str = Field(title="first_image", description="첫 번째 이미지 URL")


class RouteResGetContentList(BaseModel):
    data: list[RouteResContentSummary] = Field([], description="게시글 요약 정보 리스트")
    count: int = Field(description="현재 페이지 게시글 수")
    total: int = Field(description="전체 게시글 수")
