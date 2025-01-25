from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, status
from google.cloud.firestore_v1.base_query import BaseCompositeFilter, FieldFilter
from google.cloud.firestore_v1.client import Client
from zoneinfo import ZoneInfo

from database import get_firestore_client
from domain.schema.content_schemas import (
    RouteReqPostContent,
    RouteReqPutContent,
    RouteResContentSummary,
    RouteResGetContent,
    RouteResGetContentDetail,
    RouteResGetContentList,
)


async def service_get_content(
    post_number: int,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContent:
    # Query for the document with matching post_number and not deleted
    contents_query = (
        db.collection("contents")
        .where(
            filter=BaseCompositeFilter(
                "AND", [
                    FieldFilter("post_number", "==", post_number),
                    FieldFilter("is_deleted", "==", False)
                ]
            )
        )
        .limit(1)
    )
    contents = contents_query.get()

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    content_doc = contents[0]
    content_data = content_doc.to_dict()

    response = RouteResGetContent(
        content_id=content_doc.id,
        post_number=content_data["post_number"],
        title=content_data["title"],
        contents=content_data["contents"],
        images=content_data["images"],
        updated_at=content_data["updated_at"],
    )
    return response


async def service_get_content_list(
    page: int,
    limit: int,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContentList:
    # Calculate offset for pagination
    offset = (page - 1) * limit

    # Get total count of non-deleted contents
    total_query = db.collection("contents").where(filter=FieldFilter("is_deleted", "==", False))
    total_docs = total_query.get()
    total_count = len(list(total_docs))

    # Get paginated contents
    contents_query = (
        db.collection("contents")
        .where(filter=FieldFilter("is_deleted", "==", False))
        .order_by("post_number", direction="DESCENDING")
        .offset(offset)
        .limit(limit)
    )
    contents = contents_query.get()

    content_list = []
    for content in contents:
        content_data = content.to_dict()
        content_list.append(
            RouteResContentSummary(
                content_id=content.id,
                post_number=content_data["post_number"],
                title=content_data["title"],
                first_image=content_data["images"][0] if content_data["images"] else ""
            )
        )

    return RouteResGetContentList(
        data=content_list,
        count=len(content_list),
        total=total_count
    )


async def service_create_content(
    content: RouteReqPostContent,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContent:
    # Get the next post number
    contents_ref = db.collection("contents")
    latest_content = contents_ref.order_by("post_number", direction="DESCENDING").limit(1).get()
    next_post_number = 1
    if latest_content and len(latest_content) > 0:
        next_post_number = latest_content[0].to_dict().get("post_number", 0) + 1
        """재설계 필요"""

    # Get current timestamp in KST
    now = datetime.now(ZoneInfo("Asia/Seoul"))

    # Prepare content data
    content_data = content.model_dump()
    content_data.update({
        "post_number": next_post_number,
        "created_at": now,
        "updated_at": now,
        "is_deleted": False
    })

    # Create the document with auto-generated ID
    doc_ref = contents_ref.document()
    doc_ref.set(content_data)

    return RouteResGetContent(
        content_id=doc_ref.id,
        **content_data
    )


async def service_update_content(
    post_number: int,
    request: RouteReqPutContent,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContent:
    # Query for the document with matching post_number and not deleted
    contents_query = (
        db.collection("contents")
        .where(
            filter=BaseCompositeFilter(
                "AND", [
                    FieldFilter("post_number", "==", post_number),
                    FieldFilter("is_deleted", "==", False)
                ]
            )
        )
        .limit(1)
    )
    contents = contents_query.get()

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    content_doc = contents[0]
    # Exclude None values, empty strings, and empty lists from the update
    content_data = {
        key: value for key, value in request.model_dump().items()
        if value is not None and value != "" and value != []
    }

    # Only update if there are non-empty values
    if content_data:
        content_data.update({
            "updated_at": datetime.now(ZoneInfo("Asia/Seoul"))
        })
        # Update using the correct document reference
        db.collection("contents").document(content_doc.id).update(content_data)

    # Get the updated document
    updated_doc = db.collection("contents").document(content_doc.id).get()
    return RouteResGetContent(
        content_id=content_doc.id,
        **updated_doc.to_dict()
    )


async def service_delete_content(
    post_number: int,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> None:
    # Query for the document with matching post_number and not deleted
    contents_query = (
        db.collection("contents")
        .where(
            filter=BaseCompositeFilter(
                "AND", [
                    FieldFilter("post_number", "==", post_number),
                    FieldFilter("is_deleted", "==", False)
                ]
            )
        )
        .limit(1)
    )
    contents = contents_query.get()

    if not contents or len(contents) == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Content not found"
        )

    content_doc = contents[0]
    # Update using the correct document reference
    db.collection("contents").document(content_doc.id).update({"is_deleted": True})

    return


async def service_get_content_detail(
    post_number: int,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContentDetail:
    # Query for the document with matching post_number and not deleted
    contents_query = (
        db.collection("contents")
        .where(
            filter=BaseCompositeFilter(
                "AND", [
                    FieldFilter("post_number", "==", post_number),
                    FieldFilter("is_deleted", "==", False)
                ]
            )
        )
        .limit(1)
    )
    contents = contents_query.get()

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
    )
    return response
