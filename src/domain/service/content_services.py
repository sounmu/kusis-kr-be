import time
from datetime import datetime

from fastapi import HTTPException, UploadFile, status
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_query import And, FieldFilter
from zoneinfo import ZoneInfo

from domain.schema.content_schemas import (
    RouteReqPostContent,
    RouteReqPutContent,
    RouteResContentSummary,
    RouteResGetContent,
    RouteResGetContentDetail,
    RouteResGetContentList,
)
from utils.crud_utils import FirestoreService
from utils.image_utils import ImageUploader


async def service_get_content(
    post_number: int,
    db: AsyncClient,
) -> RouteResGetContent:
    # Get document by increment ID (post_number)
    content_data = await FirestoreService(db).get_document_by_increment_id("contents", "post_number", post_number)
    if content_data is None or content_data.get("is_deleted", True):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    response = RouteResGetContent(
        content_id=content_data["document_id"],
        post_number=content_data["post_number"],
        title=content_data["title"],
        contents=content_data["contents"],
        images=content_data["images"],
        updated_at=content_data["updated_at"],
        category=content_data["category"],
    )
    return response


async def service_get_content_list(
    page: int,
    limit: int,
    category: str | None,
    db: AsyncClient,
) -> RouteResGetContentList:
    # Calculate offset for pagination
    start_time = time.time()
    offset = (page - 1) * limit

    filters = [FieldFilter("is_deleted", "==", False)]
    if category:
        filters.append(FieldFilter("category", "==", category))

    """query_start1 = time.time()
    total_query = db.collection("contents").where(filter=And(filters))
    aggregate_query = AsyncAggregationQuery(total_query)
    aggregate_query.count(alias="total")
    results = await aggregate_query.get()
    total_count = results[0][0].value
    query_end1 = time.time()

    print(f"Query time: {query_end1 - query_start1} seconds")"""

    query_start2 = time.time()
    count_query = db.collection("counters").document("contents")
    count_doc = await count_query.get()
    total_count = count_doc.to_dict()["count"]
    query_end2 = time.time()
    print(f"Query2 time: {query_end2 - query_start2} seconds")

    query_start3 = time.time()
    # Get paginated contents using And filter
    contents_query = (
        db.collection("contents")
        .where(filter=And(filters))
        .order_by("post_number", direction="DESCENDING")
        .offset(offset)
        .limit(limit)
    )
    contents = await contents_query.get()
    query_end3 = time.time()

    print(f"Query3 time: {query_end3 - query_start3} seconds")

    parse_start = time.time()
    content_list = [
        RouteResContentSummary(
            post_number=content_data["post_number"],
            title=content_data["title"],
            first_image=content_data["images"][0] if content_data["images"] else "",
            category=content_data["category"],
        )
        for content in contents
        if (content_data := content.to_dict())
    ]
    parse_end = time.time()

    print(f"Parse time: {parse_end - parse_start} seconds")

    response = RouteResGetContentList(
        data=content_list,
        count=len(content_list),
        total=total_count
    )
    total_time = time.time() - start_time
    print(f"Total time: {total_time} seconds")
    return response


async def service_create_content(
    content: RouteReqPostContent,
    images: list[UploadFile],
    db: AsyncClient,
    image_uploader: ImageUploader,
) -> RouteResGetContent:
    # Get current timestamp in KST
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    # Upload images if provided
    image_urls = []
    if images:
        image_urls = await image_uploader.upload_images(images)

    # Prepare content data
    content_data = content.model_dump()
    content_data.update({
        "created_at": now,
        "updated_at": now,
        "is_deleted": False,
        "category": content.category,
        "images": image_urls,  # 업로드된 이미지 URL 목록 저장
    })

    # Create document with auto-increment ID
    result = await FirestoreService(db).create_document_with_increment_id("contents", "post_number", content_data)
    if result is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create content"
        )

    # Update content data with the generated ID
    content_data["post_number"] = result["post_number"]

    response = RouteResGetContent(
        content_id=result["document_id"],
        **content_data
    )
    return response


async def service_update_content(
    post_number: int,
    request: RouteReqPutContent,
    db: AsyncClient,
) -> RouteResGetContent:
    # Query for the document with matching post_number and not deleted
    contents_query = (
        db.collection("contents")
        .where(
            filter=And([
                FieldFilter("post_number", "==", post_number),
                FieldFilter("is_deleted", "==", False)
            ])
        )
        .limit(1)
    )
    contents = await contents_query.get()

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    content_doc = contents[0]
    # Exclude None values, empty strings, and empty lists from the update
    content_data = {
        key: value for key, value in request.model_dump(exclude_unset=True).items()
        if value is not None and value != "" and value != []
    }

    # Only update if there are non-empty values
    if content_data:
        content_data.update({
            "updated_at": datetime.now(ZoneInfo("Asia/Seoul")),
        })
        # Update using the correct document reference with await
        await db.collection("contents").document(content_doc.id).update(content_data)

    # Get the updated document
    updated_doc = await db.collection("contents").document(content_doc.id).get()

    response = RouteResGetContent(
        content_id=content_doc.id,
        **updated_doc.to_dict()
    )
    return response


async def service_delete_content(
    post_number: int,
    db: AsyncClient,
) -> None:
    # Query for the document with matching post_number and not deleted
    contents_query = (
        db.collection("contents")
        .where(
            filter=And([
                FieldFilter("post_number", "==", post_number),
                FieldFilter("is_deleted", "==", False)
            ])
        )
        .limit(1)
    )
    contents = await contents_query.get()

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    content_doc = contents[0]
    # Update using the correct document reference with await
    await db.collection("contents").document(content_doc.id).update({"is_deleted": True})

    return


async def service_get_content_detail(
    post_number: int,
    db: AsyncClient,
) -> RouteResGetContentDetail:
    # Query for the document with matching post_number and not deleted
    contents_query = (
        db.collection("contents")
        .where(
            filter=And([
                FieldFilter("post_number", "==", post_number),
                FieldFilter("is_deleted", "==", False)
            ])
        )
        .limit(1)
    )
    contents = await contents_query.get()

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    content_doc = contents[0]
    content_data = content_doc.to_dict()

    response = RouteResGetContentDetail(
        content_id=content_doc.id,
        post_number=content_data["post_number"],
        title=content_data["title"],
        contents=content_data["contents"],
        images=content_data["images"],
        created_at=content_data["created_at"],
        updated_at=content_data["updated_at"],
        is_deleted=content_data["is_deleted"],
        category=content_data["category"],
    )
    return response
