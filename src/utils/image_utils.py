from io import BytesIO
from typing import Annotated

from fastapi import Depends, HTTPException, UploadFile, status
from google.cloud import storage
from PIL import Image

from config import settings
from database import get_storage


class ImageUploader:
    def __init__(self, storage_client: storage.Client):
        self.storage_client = storage_client
        self.bucket = self.storage_client.bucket(settings.GCS_BUCKET_NAME)
        self.allowed_types = settings.ALLOWED_IMAGE_TYPES
        self.max_size = settings.MAX_IMAGE_SIZE
        # 이미지 최적화 설정
        self.max_dimension = 1200  # 최대 너비/높이
        self.webp_quality = 50  # WebP 품질 (0-100)

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

    def optimize_image(self, image_data: bytes, content_type: str) -> tuple[bytes, str]:
        """이미지를 최적화하고 WebP로 변환합니다."""
        try:
            # 이미지 열기
            img = Image.open(BytesIO(image_data))

            # RGBA 모드인 경우 RGB로 변환
            if img.mode in ('RGBA', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[-1])
                img = background

            # 이미지 리사이징
            if img.width > self.max_dimension or img.height > self.max_dimension:
                ratio = min(self.max_dimension / img.width, self.max_dimension / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # WebP로 변환
            output = BytesIO()
            img.save(output, format='WebP', quality=self.webp_quality, optimize=True)
            optimized_data = output.getvalue()

            return optimized_data, 'image/webp'

        except Exception as e:
            print(f"Image optimization error: {str(e)}")
            # 최적화 실패 시 원본 반환
            return image_data, content_type

    async def upload_images(self, files: list[UploadFile]) -> list[str]:
        """여러 이미지를 업로드하고 GCS URL 목록을 반환합니다."""
        gcs_urls = []

        for file in files:
            try:
                # 이미지 유효성 검사
                self.validate_image(file)

                # 안전한 파일명 생성 (확장자를 webp로 변경)
                original_filename = file.filename.rsplit('.', 1)[0]
                safe_filename = self._generate_safe_filename(f"{original_filename}.webp")
                blob = self.bucket.blob(f"images/{safe_filename}")

                # 파일 내용 읽기 및 최적화
                contents = await file.read()
                optimized_contents, content_type = self.optimize_image(contents, file.content_type)

                # 최적화된 이미지 업로드
                blob.content_type = content_type
                blob.upload_from_string(
                    optimized_contents,
                    content_type=content_type
                )

                # GCS URL 생성
                gcs_url = f"https://firebasestorage.googleapis.com/v0/b/{settings.GCS_BUCKET_NAME}/o/images%2F{safe_filename}?alt=media"
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
