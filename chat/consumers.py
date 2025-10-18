import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.core.mail import send_mail
from django.conf import settings
from .models import Message, SupportSession

User = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """Підключення користувача до кімнати"""
        self.session_id = self.scope['url_route']['kwargs']['session_id']
        self.room_group_name = f'chat_{self.session_id}'

        # Перевірка авторизації користувача
        user = self.scope.get("user")
        if user is None or isinstance(user, AnonymousUser):
            await self.close(code=4001)
            return

        # Перевірка доступу користувача до сесії
        has_access = await self.check_user_access(user, self.session_id)
        if not has_access:
            await self.close()
            return

        # Додавання до групи та прийняття підключення
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        """Від'єднання користувача"""
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        """Отримання повідомлення від користувача"""
        data = json.loads(text_data)
        message = data.get('message')

        # Валідація повідомлення
        if not message or not message.strip():
            return

        user = self.scope["user"]

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

        # Надсилання email-сповіщення
        await self.send_email_notification(saved_message)

    async def chat_message(self, event):
        """Відправка повідомлення користувачам"""
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def check_user_access(self, user, session_id):
        """Перевірка доступу користувача до сесії"""
        try:
            session = SupportSession.objects.get(id=session_id)
            return session.user == user or session.agent == user
        except SupportSession.DoesNotExist:
            return False

    @database_sync_to_async
    def save_message(self, session_id, user, content):
        """Збереження повідомлення в базу даних"""
        message = Message.objects.create(
            session_id=session_id,
            sender=user,
            content=content,
            is_agent_message=user.is_staff
        )
        return message

    @database_sync_to_async
    def send_email_notification(self, message_obj):
        """Надсилання email-сповіщення про нове повідомлення"""
        try:
            session = SupportSession.objects.select_related('user', 'agent').get(
                id=message_obj.session_id
            )

            # Визначаємо отримувача (якщо відправник - агент, то отримувач - user і навпаки)
            if message_obj.sender.is_staff:
                receiver = session.user
            else:
                receiver = session.agent

            # Перевірка наявності отримувача та email
            if not receiver or not receiver.email:
                return

            subject = f"Нове повідомлення від {message_obj.sender.username}"
            body = (
                f"Ви отримали нове повідомлення від користувача {message_obj.sender.username}:\n\n"
                f"{message_obj.content}\n\n"
                "Відповісти можна у вашому акаунті."
            )

            send_mail(
                subject,
                body,
                settings.DEFAULT_FROM_EMAIL,
                [receiver.email],
                fail_silently=True,
            )
        except SupportSession.DoesNotExist:
            pass