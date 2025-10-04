import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SupportSession, SupportMessage
from django.contrib.auth import get_user_model

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'

        # Перевірка доступу користувача до сесії
        user = self.scope['user']
        if await self.check_user_access(user, self.session_id):
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
        else:
            await self.close()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']

        # Збереження повідомлення в БД
        saved_message = await self.save_message(self.session_id, user, message)

        # Відправка повідомлення всім учасникам групи
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
                'timestamp': saved_message.created_at.strftime('%d.%m.%Y %H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def check_user_access(self, user, session_id):
        try:
            session = SupportSession.objects.get(id=session_id)
            return session.user == user or session.agent == user
        except SupportSession.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, session_id, user, content):
        session = SupportSession.objects.get(id=session_id)
        message = SupportMessage.objects.create(
            session=session,
            sender=user,
            content=content,
            is_agent_message=user.is_staff
        )
        return message
