from typing import Annotated

from fastapi import Depends, HTTPException
from google.cloud.firestore_v1.client import Client

from database import get_firestore_client
from domain.schema.content_schemas import RouteResGetContent


async def service_get_content(
    content_id: int,
    db: Annotated[Client, Depends(get_firestore_client)],
) -> RouteResGetContent:
    content_doc = db.collection("contents").document(content_id).get()
    content_data = content_doc.to_dict()

    if not content_data:
        raise HTTPException(status_code=404, detail="Content not found")

    response = RouteResGetContent(
        content_id=content_id,
        title=content_data["title"],
        contents=content_data["contents"],
        images=content_data["images"],
        created_at=content_data["created_at"],
        updated_at=content_data["updated_at"],
        is_deleted=content_data["is_deleted"],
    )
    return response
