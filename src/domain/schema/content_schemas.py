from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class ContentCategory(str, Enum):
    APPLY = "apply"
    NOTICE = "notice"
    CARDNEWS = "cardnews"


class RouteReqPostContent(BaseModel):
    category: ContentCategory = Field(description="Content category")
    title: str = Field(title="title", description="게시글 제목")
    contents: str = Field(title="contents", description="게시글 내용")


class DomainReqPostContent(BaseModel):
    post_number: int = Field(title="post_number", description="게시글 Post Number")
    title: str = Field(title="title", description="게시글 제목")
    contents: str = Field(title="contents", description="게시글 내용")
    images: list[bytes] = Field([], title="images", description="이미지 모음")
    created_at: datetime = Field(datetime.now(), title="created_at", description="게시글 작성일")
    updated_at: datetime = Field(datetime.now(), title="updated_at", description="게시글 최종 수정일")
    is_deleted: bool = Field(False, title="is_deleted", description="삭제: True, 미삭제: False")


class RouteResGetContent(BaseModel):
    content_id: str = Field(title="content_id", description="게시글 ID")
    post_number: int = Field(title="post_number", description="게시글 Post Number")
    title: str = Field(title="title", description="게시글 제목")
    contents: str = Field(title="contents", description="게시글 내용")
    images: list[str] = Field([], title="images", description="이미지 URL 목록")
    updated_at: datetime = Field(datetime.now(), title="updated_at", description="게시글 최종 수정일")
    category: ContentCategory


class RouteResGetContentDetail(BaseModel):
    content_id: str = Field(title="content_id", description="게시글 ID")
    post_number: int = Field(title="post_number", description="게시글 Post Number")
    title: str = Field(title="title", description="게시글 제목")
    contents: str = Field(title="contents", description="게시글 내용")
    images_url: list[str] = Field([], title="images_url", description="이미지 URL 모음")
    created_at: datetime = Field(datetime.now(), title="created_at", description="게시글 작성일")
    updated_at: datetime = Field(datetime.now(), title="updated_at", description="게시글 최종 수정일")
    is_deleted: bool = Field(False, title="is_deleted", description="삭제: True, 미삭제: False")
    category: ContentCategory


class RouteResContentSummary(BaseModel):
    post_number: int = Field(title="post_number", description="게시글 Post Number")
    title: str = Field(title="title", description="게시글 제목")
    first_image: str = Field(title="first_image", description="첫 번째 이미지 URL")
    category: ContentCategory


class RouteResGetContentList(BaseModel):
    data: list[RouteResContentSummary] = Field([], description="게시글 요약 정보 리스트")
    count: int = Field(description="현재 페이지 게시글 수")
    total: int = Field(description="전체 게시글 수")


class RouteReqPutContent(BaseModel):
    category: ContentCategory | None = Field(None, description="Content category")
    title: str | None = Field(title="title", description="게시글 제목")
    contents: str | None = Field(title="contents", description="게시글 내용")
    images: list[bytes] | None = Field(title="images", description="이미지 모음")
