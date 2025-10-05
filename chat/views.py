from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import SupportSession, SupportMessage
from .forms import SupportSessionForm, SupportMessageForm
from django.db.models import Q
from django.utils import timezone
from .utils import send_chat_closed_email, send_agent_reply_email
from bns_goiteens.decorators import support_required


def is_support_agent(user):
    return user.is_staff


@login_required
def create_support_session(request):
    if request.method == 'POST':
        form = SupportSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            messages.success(request, 'Ваше звернення створено. Очікуйте відповіді.')
            return redirect('chat:support_session_detail', session_id=session.id)
    else:
        form = SupportSessionForm()

    return render(request, 'chat/create_support_session.html', {'form': form})


@login_required
def user_support_sessions(request):
    sessions = SupportSession.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'chat/user_support_sessions.html', {'sessions': sessions})


@login_required
def support_session_detail(request, session_id):
    session = get_object_or_404(SupportSession, id=session_id)
    if session.user != request.user and (not session.agent or session.agent != request.user):
        messages.error(request, 'У вас немає доступу до цієї сесії.')
        return redirect('chat:user_support_sessions')
    if request.method == 'POST':
        form = SupportMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.session = session
            message.sender = request.user
            message.is_agent_message = request.user.is_staff
            message.save()
            if session.status == 'pending' and message.sender == session.user:
                session.status = 'active'
                session.save()

            return redirect('chat:support_session_detail', session_id=session.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Помилка: {error}")
    else:
        form = SupportMessageForm()
    if session.agent == request.user:
        SupportMessage.objects.filter(
            session=session,
            sender=session.user,
            is_read=False
        ).update(is_read=True)
    elif session.user == request.user and session.agent:
        SupportMessage.objects.filter(
            session=session,
            sender=session.agent,
            is_read=False
        ).update(is_read=True)
    messages_list = session.messages.all()
    return render(request, 'chat/support_session_detail.html', {
        'session': session,
        'messages_list': messages_list,
        'form': form
    })


@support_required
def agent_dashboard(request):
    pending_sessions = SupportSession.objects.filter(status='pending', agent=None)
    assigned_sessions = SupportSession.objects.filter(agent=request.user).exclude(status='closed')

    return render(request, 'chat/agent_dashboard.html', {
        'pending_sessions': pending_sessions,
        'assigned_sessions': assigned_sessions
    })


@require_POST
@support_required
def assign_session(request, session_id):
    try:
        session = get_object_or_404(SupportSession, id=session_id, agent=None, status='pending')
        session.agent = request.user
        session.status = 'active'
        session.save()
        messages.success(request, f'Ви прийняли сесію #{session.id}')
    except Exception as e:
        messages.error(request, 'Не вдалося прийняти сесію. Можливо, її вже прийняв інший агент.')
    return redirect('chat:agent_dashboard')


@support_required
def agent_session_detail(request, session_id):
    session = get_object_or_404(SupportSession, id=session_id, agent=request.user)
    if request.method == 'POST':
        form = SupportMessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.session = session
            message.sender = request.user
            message.is_agent_message = True
            message.save()
            try:
                send_agent_reply_email(message)
            except Exception as e:
                pass
            return redirect('chat:agent_session_detail', session_id=session.id)
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Помилка: {error}")
    else:
        form = SupportMessageForm()
    (SupportMessage.objects.filter(
        session=session,
        sender=session.user,
        is_read=False
    )
     .update(is_read=True))
    messages_list = session.messages.all()
    return render(request, 'chat/agent_session_detail.html', {
        'session': session,
        'messages_list': messages_list,
        'form': form
    })


@require_POST
@login_required
def close_session(request, session_id):
    session = get_object_or_404(SupportSession, id=session_id)
    if session.user != request.user and session.agent != request.user:
        messages.error(request, 'У вас немає прав для закриття цієї сесії.')
        return redirect('chat:user_support_sessions')
    session.status = 'closed'
    session.closed_at = timezone.now()
    session.save()
    try:
        send_chat_closed_email(session)
    except Exception as e:
        pass
    if request.user.is_staff:
        messages.success(request, f'Сесію #{session.id} закрито.')
        return redirect('chat:agent_dashboard')
    else:
        messages.success(request, 'Вашу сесію підтримки закрито.')
        return redirect('chat:user_support_sessions')


# Додаткові функції для WebSocket підтримки
def get_unread_messages_count(request):
    """
    Отримати кількість непрочитаних повідомлень для поточного користувача
    """
    if request.user.is_authenticated:
        unread_count = SupportMessage.objects.filter(
            session__user=request.user,
            is_read=False
        ).count()
        return JsonResponse({'unread_count': unread_count})
    return JsonResponse({'unread_count': 0})


@login_required
def websocket_chat_test(request, session_id):
    session = get_object_or_404(SupportSession, id=session_id)
    if session.user != request.user and (not session.agent or session.agent != request.user):
        messages.error(request, 'У вас немає доступу до цієї сесії.')
        return redirect('chat:user_support_sessions')

    messages_list = session.messages.all().order_by('created_at')

    return render(request, 'chat/websocket_chat.html', {
        'session': session,
        'messages_list': messages_list
    })
