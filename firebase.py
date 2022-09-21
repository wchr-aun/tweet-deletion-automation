import datetime
from firebase_admin import credentials, firestore, storage, initialize_app
from decouple import config
import json
from models.tweet import Tweet


class Firebase:
    def __init__(self) -> None:
        SERVICE_ACCOUNT = config('SERVICE_ACCOUNT')
        STORAGE_BUCKET = config('STORAGE_BUCKET')
        cred = credentials.Certificate(json.loads(SERVICE_ACCOUNT))
        initialize_app(cred, {'storageBucket': STORAGE_BUCKET})
        self.db = firestore.client()
        self.storage = storage.bucket()

    def add_tweet(self, id: str, tweet: Tweet) -> bool:
        try:
            doc_ref = self.db.collection('tweets').document(id)
            doc_ref.set(tweet)
            return True
        except Exception as e:
            print("Error adding tweet:", e)
            return False

    def upload_media(self, _from: str, filename: str) -> bool:
        try:
            blob = self.storage.blob("media/" + filename)
            blob.upload_from_filename(_from)
            return True
        except Exception as e:
            print("Error uploading media:", e)
            return False

    def get_media_url(self, filename) -> str:
        blob = self.storage.get_blob(filename)
        return blob.generate_signed_url(datetime.timedelta(seconds=300), method='GET')
