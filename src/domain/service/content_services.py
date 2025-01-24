from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException
from google.cloud.firestore_v1.client import Client
from zoneinfo import ZoneInfo

from database import get_firestore_client
from domain.schema.content_schemas import (
    RouteReqPostContent,
    RouteResContentSummary,
    RouteResGetContent,
    RouteResGetContentList,
)


async def service_get_content(
    post_number: int,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContent:
    # Query for the document with matching post_number
    contents_query = db.collection("contents").where("post_number", "==", post_number).limit(1)
    contents = contents_query.get()

    if not contents or len(contents) == 0:
        raise HTTPException(status_code=404, detail="Content not found")

    content_doc = contents[0]
    content_data = content_doc.to_dict()

    response = RouteResGetContent(
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


async def service_get_content_list(
    page: int,
    limit: int,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContentList:
    # Calculate offset for pagination
    offset = (page - 1) * limit

    # Get total count of non-deleted contents
    total_query = db.collection("contents").where("is_deleted", "==", False)
    total_docs = total_query.get()
    total_count = len(list(total_docs))

    # Get paginated contents
    contents_query = (
        db.collection("contents")
        .where("is_deleted", "==", False)
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
