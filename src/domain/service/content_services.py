from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from google.cloud.firestore_v1.async_aggregation import AsyncAggregationQuery
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_query import And, FieldFilter
from zoneinfo import ZoneInfo

from database import get_async_firestore_client
from domain.schema.content_schemas import (
    RouteReqPostContent,
    RouteReqPutContent,
    RouteResContentSummary,
    RouteResGetContent,
    RouteResGetContentDetail,
    RouteResGetContentList,
)
from utils.crud_utils import FirestoreService


async def service_get_content(
    post_number: int,
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
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
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
) -> RouteResGetContentList:
    # Calculate offset for pagination
    offset = (page - 1) * limit

    filters = [FieldFilter("is_deleted", "==", False)]
    if category:
        filters.append(FieldFilter("category", "==", category))

    total_query = db.collection("contents").where(filter=And(filters))
    aggregate_query = AsyncAggregationQuery(total_query)
    aggregate_query.count(alias="total")
    results = await aggregate_query.get()

    total_count = results[0][0].value

    # Get paginated contents using And filter
    contents_query = (
        db.collection("contents")
        .where(filter=And(filters))
        .order_by("post_number", direction="DESCENDING")
        .offset(offset)
        .limit(limit)
    )
    contents = await contents_query.get()

    content_list = [
        RouteResContentSummary(
            content_id=content.id,
            post_number=content_data["post_number"],
            title=content_data["title"],
            first_image=content_data["images"][0] if content_data["images"] else "",
            category=content_data["category"],
        )
        for content in contents
        if (content_data := content.to_dict())
    ]

    response = RouteResGetContentList(
        data=content_list,
        count=len(content_list),
        total=total_count
    )
    return response


async def service_create_content(
    content: RouteReqPostContent,
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
) -> RouteResGetContent:
    # Get current timestamp in KST
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    # Prepare content data
    content_data = content.model_dump()
    content_data.update({
        "created_at": now,
        "updated_at": now,
        "is_deleted": False,
        "category": content.category,
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
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
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
            "category": request.category,
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
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
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
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
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
