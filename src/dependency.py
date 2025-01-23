from typing import Any, Dict

from fastapi import Depends, Header, HTTPException, status
from jose import jwt
from jwt import PyJWTError

from config import Settings
from database import get_firestore_client
from exception import InactiveUserException


async def get_current_user(token=Header(None)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid credentials",
        headers={"WW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, key=Settings().JWT_SECRET_KEY, algorithms=Settings().JWT_ALGORITHM)
        user_id: int = int(payload.get("sub"))

        if not isinstance(user_id, int) or user_id <= 0:
            raise credentials_exception

        db = get_firestore_client()
        user_doc = await db.collection("users").document(user_id).get()

        if not user_doc.exists:
            raise credentials_exception

        user_data: Dict[str, Any] = user_doc.to_dict()

        if not user_data["is_verified"]:
            raise credentials_exception

        return user_data
    except PyJWTError as e:
        raise credentials_exception from e


def get_current_active_user(user: Dict[str, Any]= Depends(get_current_user)):
    if not user.get("is_active"):
        raise InactiveUserException()
    return user
