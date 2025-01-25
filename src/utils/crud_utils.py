from google.cloud.firestore import DocumentReference
from google.cloud.firestore_v1.async_client import AsyncClient
from google.cloud.firestore_v1.base_query import And, FieldFilter

from domain.service.counter_services import get_async_next_id


class FirestoreService:
    def __init__(self, db: AsyncClient):
        self.db = db


    async def create_document_with_increment_id(
        self,
        collection_name: str,
        key_name: str,
        data: dict[str, object],
    ) -> dict[str, object] | None:
        next_id = await get_async_next_id(collection_name, self.db)
        if next_id is None:
            return None

        try:
            doc_ref: DocumentReference = self.db.collection(collection_name).document()
            data[f"{key_name}"] = next_id
            batch = self.db.batch()
            batch.set(doc_ref, data)
            await batch.commit() # 비동기 commit 호출
            return {"document_id": doc_ref.id, f"{key_name}": next_id}
        except Exception as e:
            print(f"Error creating document: {e}")
            return None


    async def get_document_by_increment_id(
        self,
        collection_name: str,
        key_name: str,
        increment_id: int,
    ) -> dict[str, object] | None:
        try:
            query = (
                self.db.collection(collection_name)
                .where(
                    filter=And([
                        FieldFilter(f"{key_name}", "==", increment_id),
                        FieldFilter("is_deleted", "==", False)
                    ])
                )
                .limit(1)
            )
            result = await query.get()
            if result:
                document = result[0]
                data = document.to_dict()
                data['document_id'] = document.id  # 문서 ID를 딕셔너리에 추가
                return data
            return None
        except Exception as e:
            print(f"Error fetching document: {e}")
            return None
