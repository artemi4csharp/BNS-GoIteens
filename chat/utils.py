import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

logger = logging.getLogger(__name__)

def send_chat_closed_email(session):
    try:
        subject = f"Ваш чат підтримки #{session.id} було закрито"
        messages = session.messages.all().order_by('created_at')
        context = {
            'session': session,
            'messages': messages,
            'user': session.user,
        }
        html_message = render_to_string('chat/chat_closed.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [session.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Відправлено лист про закриття чату користувачу {session.user.email}")
    except Exception as e:
        logger.error(f"Помилка при відправці листа про закриття чату: {str(e)}")
        raise

def send_agent_reply_email(message):
    try:
        session = message.session
        subject = f"Нова відповідь у чаті підтримки #{session.id}"
        context = {
            'session': session,
            'message': message,
            'user': session.user,
        }
        html_message = render_to_string('chat/agent_reply.html', context)
        plain_message = strip_tags(html_message)
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            [session.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        logger.info(f"Відправлено лист про нове повідомлення агента користувачу {session.user.email}")
    except Exception as e:
        logger.error(f"Помилка при відправці листа про нове повідомлення: {str(e)}")
        raise
