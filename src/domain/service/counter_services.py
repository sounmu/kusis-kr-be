# services/counter_service.py
import asyncio
from typing import Annotated

from fastapi import Depends
from google.api_core.exceptions import GoogleAPICallError, RetryError
from google.cloud.firestore_v1.async_client import AsyncClient

from database import get_async_firestore_client


async def get_async_next_id(
    collection_name: str,
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)]
) -> int | None:
    counter_ref = db.collection("counters").document(collection_name)
    max_retries = 5
    base_delay = 0.1  # 100ms
    async def attempt_transaction() -> int:
        transaction = db.transaction()
        await transaction._begin()

        # Get the current counter value
        snapshot = await counter_ref.get(transaction=transaction)
        if snapshot.exists:
            current_count = snapshot.to_dict().get('count', 0)
            next_id = current_count + 1
            transaction.update(counter_ref, {"count": next_id})
        else:
            next_id = 1
            transaction.set(counter_ref, {"count": next_id})

        # Commit the transaction
        await transaction._commit()
        return next_id

    for attempt in range(max_retries):
        try:
            return await attempt_transaction()
        except (GoogleAPICallError, RetryError) as e:
            # Handle specific Firestore exceptions
            if attempt == max_retries - 1:
                print(f"Firestore transaction error after {max_retries} attempts: {e}")
                return None
            # Exponential backoff with jitter
            delay = base_delay * (2 ** attempt) * (0.5 + asyncio.random.random())
            await asyncio.sleep(delay)
        except Exception as e:
            # Handle any other exceptions
            print(f"Unexpected error: {e}")
            return None
    return None
