import firebase_admin
from firebase_admin import credentials, auth

cred = credentials.Certificate('photosharingapp/firebase-service-account-key.json')
firebase_admin.initialize_app(cred)


class AuthenticationService():
    def create_new_user(self, user):
        user = auth.create_user(**user)
        return user

    def generate_new_token(self, uid: str) -> str:
        token = auth.create_custom_token(uid)
        return token

    def verify_token(self, token: str) -> str:
        decoded_token = auth.verify_id_token(token)
        return decoded_token['uid']


authentication_service: AuthenticationService = AuthenticationService()


