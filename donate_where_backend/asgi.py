"""
ASGI config for donate_where_backend project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""
import os

from channels.routing import URLRouter, ProtocolTypeRouter

from .token_auth_middleware import token_aut_middleware_stack
from .routing import websocket_urlpatterns

from django.core.asgi import get_asgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'donate_where_backend.settings')

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': token_aut_middleware_stack(URLRouter(websocket_urlpatterns))
})
