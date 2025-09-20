
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from .models import Message

@login_required
def send_message(request, user_id):
    receiver = get_object_or_404(User, id=user_id)

    if request.method == "POST":
        content = request.POST.get("content")
        if content:
            Message.objects.create(
                content=content,
                sender=request.user,
                receiver=receiver
            )
            return redirect("chat", user_id=receiver.id)

    return render(request, "chat/send_message.html", {"receiver": receiver})


@login_required
def chat(request, user_id):
    other_user = get_object_or_404(User, id=user_id)

    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by("created_at")

    return render(request, "chat/chat.html", {
        "messages": messages,
        "other_user": other_user
    })
