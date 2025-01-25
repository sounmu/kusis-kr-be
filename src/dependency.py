from typing import Any, Dict

from fastapi import Depends, Header, HTTPException, status
from google.cloud.firestore_v1.async_client import AsyncClient
from jose import jwt
from jwt import PyJWTError

from config import Settings
from database import get_async_firestore_client
from exception import InactiveUserException


async def get_current_admin(
    token: str = Header(None),
    db: AsyncClient = Depends(get_async_firestore_client)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, key=Settings().JWT_SECRET_KEY, algorithms=Settings().JWT_ALGORITHM)
        user_id: str = payload.get("sub")

        user_doc = db.collection("users").document(user_id).get()

        if not user_doc.exists:
            raise credentials_exception

        user_data: Dict[str, Any] = user_doc.to_dict()

        if not user_data["is_admin"]:
            raise credentials_exception

        return user_data
    except PyJWTError as e:
        raise credentials_exception from e


def get_current_active_admin(user: Dict[str, Any]= Depends(get_current_admin)):
    if not user.get("is_active"):
        raise InactiveUserException()
    return user
