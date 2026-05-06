"""
RemoteJWTAuthentication
-----------------------
Validates the JWT access token issued by auth_service locally
(same SECRET_KEY / HS256 algorithm).

The token payload contains:  user_id, email, token_type
We build a lightweight AuthUser object so request.user works
throughout the service without a local User table.
"""

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class AuthUser:
    """
    Lightweight user object populated from JWT claims.
    No database hit — the auth_service is the source of truth for identity.
    """
    def __init__(self, user_id, email):
        self.id = user_id
        self.pk = user_id          # DRF sometimes uses .pk
        self.email = email
        self.is_authenticated = True
        self.is_anonymous = False

    def __str__(self):
        return self.email


class RemoteJWTAuthentication(BaseAuthentication):
    """
    Reads the Bearer token from the Authorization header,
    decodes it with the shared secret, and returns an AuthUser.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header.startswith('Bearer '):
            return None  # Let DRF raise 401 via permission classes

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

        # SimpleJWT stores user_id as 'user_id' in the payload
        user_id = payload.get('user_id')
        email = payload.get('email', '')  # auth_service may or may not include email

        if not user_id:
            raise AuthenticationFailed('Token payload missing user_id.')

        return (AuthUser(user_id=int(user_id), email=email), token)

    def authenticate_header(self, request):
        return 'Bearer'