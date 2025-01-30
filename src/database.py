import os

import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore, storage
from google.oauth2 import service_account


def initialize_firebase_admin():
    if not firebase_admin._apps:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        key_path = os.path.join(current_dir, "kusis-kr-firebase-adminsdk.json")

        if not os.path.exists(key_path):
            raise FileNotFoundError(f"서비스 계정 키 파일을 찾을 수 없습니다: {key_path}")

        cred = credentials.Certificate(key_path)
        firebase_admin.initialize_app(cred)


def get_async_firestore_client() -> firestore.AsyncClient:
    initialize_firebase_admin()
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_dir, "kusis-kr-firebase-adminsdk.json")
    creds = service_account.Credentials.from_service_account_file(key_path)
    return firestore.AsyncClient(credentials=creds)


def get_auth_client():
    return auth.Client(firebase_admin.get_app())


async def get_storage() -> storage.Client:
    """Get Google Cloud Storage client."""
    current_dir = os.path.dirname(os.path.abspath(__file__))
    key_path = os.path.join(current_dir, "kusis-kr-firebase-adminsdk.json")
    creds = service_account.Credentials.from_service_account_file(key_path)

    # service account key에서 project_id를 가져와서 사용
    return storage.Client(
        credentials=creds,
        project=creds.project_id
    )
