import aiohttp
from fastapi import HTTPException, status
from firebase_admin.exceptions import FirebaseError

from config import settings
from database import get_auth_client, get_firestore_client
from domain.schema.auth_schemas import RouteResAdminLogin
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

        # Admin SDK로 사용자 정보 확인
        auth_client = get_auth_client()
        user = await auth_client.get_user(user_id)

        # Firestore에서 관리자 권한 확인
        db = get_firestore_client()
        admin_doc = await db.collection("users").document(user.uid).get()

        if not admin_doc.exists:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User not found"
            )

        admin_data = admin_doc.to_dict()
        if not admin_data.get("is_admin", False):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User is not an admin"
            )

        # JWT 토큰 생성
        access_token = await create_user_tokens(user.uid)

        return RouteResAdminLogin(
            access_token=access_token
        )

    except FirebaseError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        ) from e
