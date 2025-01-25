from datetime import datetime
from typing import Annotated

import aiohttp
from fastapi import Depends, HTTPException, status
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from google.cloud.firestore_v1.async_client import AsyncClient
from zoneinfo import ZoneInfo

from config import settings
from database import get_async_firestore_client, get_auth_client
from domain.schema.auth_schemas import (
    RouteReqUpdateUser,
    RouteResGetUser,
    RouteResLoginAdmin,
    RouteResRegisterUser,
    RouteResUpdateUser,
)
from domain.service.token_services import create_user_tokens


async def service_login_admin(
    email: str,
    password: str
) -> RouteResLoginAdmin:
    try:
        # Firebase Auth REST API를 통한 이메일/비밀번호 검증
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={settings.FIREBASE_WEB_API_KEY}"

        async with aiohttp.ClientSession() as session:
            async with session.post(auth_url, json={
                "email": email,
                "password": password,
                "returnSecureToken": True
            }) as response:
                if response.status != 200:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials"
                    )
                auth_data = await response.json()
                user_id = auth_data["localId"]

        # Firestore 비동기 조회로 수정
        db = get_async_firestore_client()
        admin_doc = await db.collection("users").document(user_id).get()

        if not admin_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        admin_data = admin_doc.to_dict()
        if not admin_data.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an admin"
            )

        # JWT 토큰 생성
        tokens = create_user_tokens(user_id)

        return RouteResLoginAdmin(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

    except FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        ) from e


async def service_register_user(
    email: str,
    password: str,
    name: str,
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
) -> RouteResRegisterUser:
    try:
        # Create user in Firebase Auth
        auth_client = get_auth_client()
        user = auth_client.create_user(
            email=email,
            password=password,
            display_name=name
        )

        # Create user document in Firestore
        now = datetime.now(ZoneInfo("Asia/Seoul"))
        user_data = {
            "email": email,
            "name": name,
            "created_at": now,
            "updated_at": now,
            "is_admin": False,
            "is_active": True,
            "is_deleted": False
        }

        # Firestore 비동기 작업으로 수정
        await db.collection("users").document(user.uid).set(user_data)

        return RouteResRegisterUser(
            email=email,
            name=name
        )

    except auth.EmailAlreadyExistsError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        ) from e
    except FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        ) from e


async def service_get_user(
    uid: str,
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
) -> RouteResGetUser:
    user_doc = await db.collection("users").document(uid).get()
    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    user_data = user_doc.to_dict()
    return RouteResGetUser(
        email=user_data["email"],
        name=user_data["name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"],
        is_admin=user_data["is_admin"],
        is_active=user_data["is_active"],
        is_deleted=user_data["is_deleted"]
    )


async def service_update_user(
    uid: str,
    request: RouteReqUpdateUser,
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
) -> RouteResUpdateUser:
    """
    Update user information in Firestore.
    Args:
        uid: User ID to update
        request: Update request containing fields to update
        db: Firestore client

    Returns:
        Updated user information

    Raises:
        NotFoundError: If user does not exist
    """
    user_ref = db.collection("users").document(uid)
    user_doc = await user_ref.get()

    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    update_data = {}
    if request.name is not None:
        update_data["name"] = request.name
    if request.is_admin is not None:
        update_data["is_admin"] = request.is_admin
    if request.is_active is not None:
        update_data["is_active"] = request.is_active

    update_data["updated_at"] = datetime.now()

    await user_ref.update(update_data)

    updated_doc = await user_ref.get()
    user_data = updated_doc.to_dict()

    return RouteResUpdateUser(
        email=user_data["email"],
        name=user_data["name"],
        created_at=user_data["created_at"],
        updated_at=user_data["updated_at"],
        is_admin=user_data["is_admin"],
        is_active=user_data["is_active"],
        is_deleted=user_data["is_deleted"]
    )


async def service_delete_user(
    uid: str,
    db: Annotated[AsyncClient, Depends(get_async_firestore_client)],
) -> None:
    user_ref = db.collection("users").document(uid)
    user_doc = await user_ref.get()

    if not user_doc.exists:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Firestore 비동기 업데이트로 수정
    await user_ref.update({"is_deleted": True})

    return
