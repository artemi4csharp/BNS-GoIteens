import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from .models import SupportSession, SupportMessage
from django.contrib.auth import get_user_model

User = get_user_model()
from django.contrib.auth.models import AnonymousUser
from django.core.mail import send_mail
from django.conf import settings
from .models import Message, User


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'
        """Підключення користувача до кімнати"""
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

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
        user = self.scope.get("user")
        if user is None or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Від'єднання користувача"""
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Отримання повідомлення від користувача"""
        data = json.loads(text_data)
        message = data['message']
        user = self.scope['user']
        message = data.get('message')

        if not message or not message.strip():
            return

        # Збереження повідомлення в БД
        saved_message = await self.save_message(self.session_id, user, message)
        user = self.scope["user"]

        # Відправка повідомлення всім учасникам групи
        # Зберігаємо повідомлення
        msg = await self.save_message(user, self.room_name, message)

        # Відправляємо повідомлення всім учасникам кімнати
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': user.username,
                'timestamp': saved_message.created_at.strftime('%d.%m.%Y %H:%M'),
                'message': message,
            }
        )

        # Надсилаємо лист на пошту отримувачу
        await self.send_email_notification(msg)

    async def chat_message(self, event):
        """Відправка повідомлення користувачам"""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
            'message': event['message']
        }))

    @database_sync_to_async
    def save_message(self, user, room, message):
        return Message.objects.create(sender=user, room_name=room, text=message)

    @database_sync_to_async
    def send_email_notification(self, message_obj):
        """Надсилання листа про нове повідомлення"""
    def check_user_access(self, user, session_id):
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
        if receiver.email:
            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [receiver.email],
                fail_silently=True,
            )

