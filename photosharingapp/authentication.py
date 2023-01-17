from django.contrib.auth.models import User
from rest_framework import authentication
from rest_framework import exceptions
from .authentication_service import authentication_service

class UserAuthentication(authentication.BaseAuthentication):

    def authenticate(self, request):
        header = authentication.get_authorization_header(request).decode()
        print(header)
        if header is None:
            return None
        elif not header.startswith('Bearer '):
            return None
        token = header.split(" ")[1]
        uid: str = authentication_service.verify_token(token)
        user = User.objects.get(profile__uid=uid)
        return user, uid



