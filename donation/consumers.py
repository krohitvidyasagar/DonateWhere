import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Message, Conversation
from .serializers import MessageSerializer


class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.room_name = self.scope['claims']['id']
        self.room_group_name = f"chat_{self.room_name}"

        # Join room group
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name, self.channel_name
        )
        self.accept()

        self.send(text_data=json.dumps({'status': 'connected'}))

    def disconnect(self, close_code):
        self.send(text_data=json.dumps({'status': 'Disconnecting'}))

        # Leave room group
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name, self.channel_name
        )

    def send_notification(self, event: dict):
        data = json.loads(event.get('data'))
        self.send(text_data=json.dumps({'payload': data}))
