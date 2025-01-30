from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from dependency import get_image_uploader
from utils.image_utils import ImageUploader

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)


@router.post(
    "/upload",
    summary="이미지 업로드",
    description="""이미지를 업로드합니다.""",
    status_code=status.HTTP_201_CREATED,
)
async def upload_images(
    image_uploader: Annotated[ImageUploader, Depends(get_image_uploader)],
    images: list[UploadFile] = File(None),
) -> list[str]:
    response = await image_uploader.upload_images(images)

    return response
