import json
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from donation.models import Message


class WebsocketUtils:

    @classmethod
    def send_chat_notification(cls, message: Message):
        sender_id = str(message.sender.id)

        sender_email = message.sender.email
        sender_name = message.sender.first_name
        conversation_id = str(message.conversation.id)
        message_text = message.text

        if sender_id == message.conversation.initiator.id:
            receiver_id = str(message.conversation.receiver.id)
        else:
            receiver_id = str(message.conversation.initiator.id)

        channel_name = f'chat_{receiver_id}'

        notification_object = {
            'sender_email': sender_email,
            'sender_name': sender_name,
            'conversation_id': conversation_id,
            'message': message_text
        }

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(channel_name, {
            'type': 'send_notification',
            'data': json.dumps(notification_object)
        })
