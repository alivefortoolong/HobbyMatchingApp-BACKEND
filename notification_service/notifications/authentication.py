import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class AuthUser:
    def __init__(self, user_id, email):
        self.id = user_id
        self.pk = user_id
        self.email = email
        self.is_authenticated = True
        self.is_anonymous = False

    def __str__(self):
        return self.email


class RemoteJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET_KEY,
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        user_id = payload.get('user_id')
        email   = payload.get('email', '')

        if not user_id:
            raise AuthenticationFailed('Token payload missing user_id.')

        return (AuthUser(user_id=int(user_id), email=email), token)

    def authenticate_header(self, request):
        return 'Bearer'