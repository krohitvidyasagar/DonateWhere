import jwt
from donate_where_backend import settings

from channels.auth import AuthMiddlewareStack
from django.contrib.auth.models import AnonymousUser

from jwt import ExpiredSignatureError, PyJWTError
from rest_framework.exceptions import NotAuthenticated, PermissionDenied, AuthenticationFailed


class JwtUtils:

    @staticmethod
    def get_claims(token):
        try:
            claims_obj = jwt.decode(token[7:], settings.JWTConfig['SIGNING_KEY'],
                                    algorithms=settings.JWTConfig['ALGORITHM'])
        except ExpiredSignatureError as e:
            raise NotAuthenticated(detail='Token has expired')
        except PyJWTError as e:
            raise PermissionDenied(detail='Token not valid')
        except KeyError as e:
            raise PermissionDenied(detail='Claims not present')
        return claims_obj


class TokenAuthMiddleware:

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        query_string = scope['query_string'].decode()

        if query_string and query_string.startswith('token='):
            try:
                token = f'Bearer {query_string[6:]}'
                claims = JwtUtils.get_claims(token)['claims']

                scope['claims'] = claims
            except AuthenticationFailed:
                scope['claims'] = AnonymousUser()
        else:
            scope['claims'] = AnonymousUser()
        return await self.inner(scope, receive, send)

def token_aut_middleware_stack(inner): return TokenAuthMiddleware(AuthMiddlewareStack(inner))
