from datetime import datetime

import aiohttp
from fastapi import HTTPException, status
from firebase_admin import auth
from firebase_admin.exceptions import FirebaseError
from zoneinfo import ZoneInfo

from config import settings
from database import get_auth_client, get_firestore_client
from domain.schema.auth_schemas import RouteResAdminLogin, RouteResUserRegister
from domain.service.token_services import create_user_tokens


async def service_admin_login(
    email: str,
    password: str
) -> RouteResAdminLogin:
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

        # Firestore에서 관리자 권한 확인
        db = get_firestore_client()
        admin_doc = db.collection("users").document(user_id).get()

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

        return RouteResAdminLogin(
            access_token=tokens["access_token"],
            refresh_token=tokens["refresh_token"],
        )

    except FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        ) from e


async def service_user_register(
    email: str,
    password: str,
    name: str
) -> RouteResUserRegister:
    try:
        # Create user in Firebase Auth
        auth_client = get_auth_client()
        user = auth_client.create_user(
            email=email,
            password=password,
            display_name=name
        )

        # Get Firestore client
        db = get_firestore_client()

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

        # Set document with user's UID as the document ID
        db.collection("users").document(user.uid).set(user_data)

        return RouteResUserRegister(
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
