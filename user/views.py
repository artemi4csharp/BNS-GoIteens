from django.shortcuts import render, redirect, get_object_or_404
from bns_goiteens.models import Block
from django.contrib.auth.decorators import login_required

from blacklist.bns_goiteens.models import User


@login_required
def block_user(request, user_id):
    user_to_block = get_object_or_404(User, id=user_id)

    if user_to_block.user != request.user:
        Block.objects.get_or_create(blocker=user_to_block, blocked=user_to_block)

    return redirect('user_profile', user_id=user_id)

@login_required
def unblock_user(request, user_id):
    user_to_unblock = get_object_or_404(User, pk=user_id)
    Block.objects.filter(blocker=user_to_unblock, blocked=user_to_unblock).delete()
    return redirect('user_profile', user_id=user_id)

@login_required
def blacklist_view(request):
    blocked_users = Block.objects.filter(blocker=request.user)
    return render(request, 'blacklist.html', {'blocked_users': blocked_users})
