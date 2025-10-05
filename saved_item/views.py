from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from bns_goiteens.models import SavedItem, Item, Service
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages

@login_required
def list_saved(request):
    saved_items = SavedItem.objects.filter(user=request.user).all()
    return render(request, 'saved_items_list.html', {"saved_items" : saved_items})


@login_required
def save_item(request, object_id, content_type):
    ct = get_object_or_404(ContentType, pk=content_type)

    _, created = SavedItem.objects.get_or_create(
        user=request.user,
        content_type=ct,
        object_id=object_id,
    )

    if created:
        messages.success(request, "Цей товар додано в збережене.")
    else:
        messages.info(request, "Цей товар уже додано в збережене.")

    return redirect('bns:home')


@login_required
def delete_saved(request, pk):
    
    saved = get_object_or_404(SavedItem, pk=pk)
    saved.delete()
    
    return redirect('saved_list')
    