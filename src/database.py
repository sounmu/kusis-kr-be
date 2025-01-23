import firebase_admin
from firebase_admin import auth, credentials, firestore

cred = credentials.Certificate("kusis-kr-firebase-adminsdk.json")
firebase_admin.initialize_app(cred)

db = firestore.client()
auth_client = auth.Client(firebase_admin.get_app())
