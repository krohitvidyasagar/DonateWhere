import bcrypt
import jwt
from datetime import datetime

from django.conf import settings

from donation.serializers import UserLoginSerializer


class AuthenticationUtils:
    bcrypt_salt = b'$2b$12$Lr2f5Vp8q5yn3tYr.AD2Uu'

    @classmethod
    def get_user_claims(cls, authenticated_user):
        return {
            'claims': UserLoginSerializer(authenticated_user).data
        }

    @classmethod
    def get_bcrypt_salt(cls):
        return cls.bcrypt_salt

    @classmethod
    def get_hashed_password(cls, password):
        return bcrypt.hashpw(password, cls.bcrypt_salt)

    @classmethod
    def get_user_access_token(cls, user_claims):
        claims_obj = {
            **user_claims,
            'type': 'access',
            'exp': datetime.utcnow() + settings.JWTConfig['ACCESS_TOKEN_LIFETIME']
        }

        return jwt.encode(claims_obj, settings.JWTConfig['SIGNING_KEY'], settings.JWTConfig['ALGORITHM'])

    @classmethod
    def get_user_refresh_token(cls, user_claims):
        claims_obj = {
            **user_claims,
            'type': 'refresh',
            'exp': datetime.utcnow() + settings.JWTConfig['REFRESH_TOKEN_LIFETIME']
        }

        return jwt.encode(claims_obj, settings.JWTConfig['SIGNING_KEY'], settings.JWTConfig['ALGORITHM'])