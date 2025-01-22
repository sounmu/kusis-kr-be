from firebase_admin import firestore

from src.domain.schema.content_schemas import RouteResGetContent


async def service_get_content(
    content_id: int,
    db: firestore.client,
) -> RouteResGetContent:
    content_doc = db.collection("contents").document(content_id).get()
    content_data = content_doc.to_dict()

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
