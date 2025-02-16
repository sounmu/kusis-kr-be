import os

import firebase_admin
from firebase_admin import auth, credentials
from google.cloud import firestore, storage
from google.oauth2 import service_account

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
KEY_PATH = os.path.join(CURRENT_DIR, "kusis-kr-firebase-adminsdk.json")

if not os.path.exists(KEY_PATH):
    raise FileNotFoundError(f"서비스 계정 키 파일을 찾을 수 없습니다: {KEY_PATH}")

GLOBAL_CREDS = service_account.Credentials.from_service_account_file(KEY_PATH)

if not firebase_admin._apps:
    cred = credentials.Certificate(KEY_PATH)
    firebase_admin.initialize_app(cred, {
        'encoding': 'utf-8'
    })

_firestore_client = firestore.AsyncClient(credentials=GLOBAL_CREDS)
_storage_client = storage.Client(
    credentials=GLOBAL_CREDS,
    project=GLOBAL_CREDS.project_id
)


def get_async_firestore_client() -> firestore.AsyncClient:
    """
    애플리케이션 전체에서 재사용 가능한 Firestore Async Client를 반환합니다.
    """
    return _firestore_client


def get_auth_client():
    """
    애플리케이션 전체에서 재사용 가능한 Auth Client를 반환합니다.
    """
    return auth


async def get_storage() -> storage.Client:
    """
    애플리케이션 전체에서 재사용 가능한 Google Cloud Storage Client를 반환합니다.
    """
    return _storage_client
