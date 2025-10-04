import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import AnonymousUser
from django.core.mail import send_mail
from django.conf import settings
from .models import Message, User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Підключення користувача до кімнати"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        user = self.scope.get("user")
        if user is None or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Від'єднання користувача"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        """Отримання повідомлення від користувача"""
        data = json.loads(text_data)
        message = data.get('message')

        if not message or not message.strip():
            return

        user = self.scope["user"]

        # Зберігаємо повідомлення
        msg = await self.save_message(user, self.room_name, message)

        # Відправляємо повідомлення всім учасникам кімнати
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': user.username,
                'message': message,
            }
        )

        # Надсилаємо лист на пошту отримувачу
        await self.send_email_notification(msg)

    async def chat_message(self, event):
        """Відправка повідомлення користувачам"""
        await self.send(text_data=json.dumps({
            'username': event['username'],
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, user, room, message):
        return Message.objects.create(sender=user, room_name=room, text=message)

    @database_sync_to_async
    def send_email_notification(self, message_obj):
        """Надсилання листа про нове повідомлення"""
        try:
            receiver = User.objects.get(id=int(message_obj.room_name))
        except (User.DoesNotExist, ValueError):
            return

        subject = f"Нове повідомлення від {message_obj.sender.username}"
        body = (
            f"Ви отримали нове повідомлення від користувача {message_obj.sender.username}:\n\n"
            f"{message_obj.text}\n\n"
            "Відповісти можна у вашому акаунті."
        )

        if receiver.email:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [receiver.email],
                fail_silently=True,
            )

