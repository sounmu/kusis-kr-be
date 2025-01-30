from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile, status
from google.cloud import storage

from config import settings
from database import get_storage


class ImageUploader:
    def __init__(self, storage_client: storage.Client):
        self.storage_client = storage_client
        self.bucket = self.storage_client.bucket(settings.GCS_BUCKET_NAME)
        self.allowed_types = settings.ALLOWED_IMAGE_TYPES
        self.max_size = settings.MAX_IMAGE_SIZE

    def validate_image(self, file: UploadFile) -> None:
        """이미지 파일의 크기와 타입을 검증합니다."""
        # 파일 타입 검증
        if file.content_type not in self.allowed_types:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Unsupported file type. Allowed types: {', '.join(self.allowed_types)}"
            )

        # 파일 크기 검증
        file.file.seek(0, 2)
        file_size = file.file.tell()
        file.file.seek(0)

        if file_size > self.max_size:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File size too large. Maximum size allowed: {self.max_size/1024/1024}MB"
            )

    def _generate_safe_filename(self, original_filename: str) -> str:
        """안전한 파일 이름을 생성합니다."""
        import re
        import uuid
        from datetime import datetime

        # 파일 확장자 추출
        ext = original_filename.rsplit('.', 1)[-1].lower() if '.' in original_filename else ''

        # 원본 파일명에서 특수문자 제거
        safe_basename = re.sub(r'[^a-zA-Z0-9.]', '', original_filename.rsplit('.', 1)[0])

        # 파일명이 너무 길 경우 잘라내기
        safe_basename = safe_basename[:50]

        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')

        # 안전한 파일명-타임스탬프-UUID.확장자 형식으로 반환
        return f"{safe_basename}-{timestamp}-{uuid.uuid4().hex[:8]}.{ext}"

    async def upload_images(self, files: list[UploadFile]) -> list[str]:
        """여러 이미지를 업로드하고 GCS URL 목록을 반환합니다."""
        gcs_urls = []

        for file in files:
            try:
                # 이미지 유효성 검사
                self.validate_image(file)

                # 안전한 파일명 생성
                safe_filename = self._generate_safe_filename(file.filename)
                blob = self.bucket.blob(f"images/{safe_filename}")

                # 파일 내용 읽기 및 업로드
                contents = await file.read()
                blob.content_type = file.content_type
                blob.upload_from_string(
                    contents,
                    content_type=file.content_type
                )

                # GCS URL 생성
                gcs_url = f"https://storage.googleapis.com/{settings.GCS_BUCKET_NAME}/images/{safe_filename}"
                gcs_urls.append(gcs_url)

            except Exception as e:
                print(f"Image upload error: {str(e)}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to upload image: {file.filename}"
                ) from e

        return gcs_urls


async def get_image_uploader(
    storage_client: Annotated[storage.Client, Depends(get_storage)]
) -> ImageUploader:
    return ImageUploader(storage_client)
