from django.urls import path

from donation import consumers

websocket_urlpatterns = [
    path('ws/conversation/<uuid:user_id>', consumers.ChatConsumer.as_asgi()),
]
