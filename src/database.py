import firebase_admin
from firebase_admin import auth, credentials, firestore

cred = credentials.Certificate("kusis-kr-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)


def get_firestore_client():
    return firestore.client()


def get_auth_client():
    return auth.Client(firebase_admin.get_app())
