from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required 
from bns_goiteens.models import Item, Rating
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import ItemCreationForm, ItemEditForm, RatingForm, CategoryRequestForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model

def item_list(request):
    items = Item.objects.all()
    return render(request, 'items_list.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    content_type = ContentType.objects.get_for_model(Item)
    
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(content_type=content_type, object_id = item.id, user=request.user).first()

    if request.method == 'POST':
        form = RatingForm(request.POST or None,  instance = user_rating)
        # request.POST данні які користувач надіслав раніше 
        if form.is_valid() and request.user.is_authenticated:
            rating = form.save(commit=False)
            rating.user = request.user
            rating.content_object = item 
            rating.save()
            messages.success(request, 'Success')
            return redirect('item_list')
        else: 
            messages.error(request, 'Error')
    return render(request, 'item_detail.html', {'form':form})



@login_required
def create_item(request):
    if request.method == 'POST':
        form = ItemCreationForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            request.user = item.owner
            item.save() 
            messages.success(request, 'Success')
        else: 
            messages.error(request, 'Error')
    else: 
        form = ItemCreationForm()
    return render(request, 'create_item.html', {'form': form})

@login_required
def edit_item(request, pk):
    item = get_object_or_404(Item, pk=pk, owner=request.user)
    form = ItemEditForm(request.POST or None, request.FILES or None, instance=item)
    if form.is_valid():
        form.save()
        messages.success(request, 'Success')
        return redirect('item_list')
    return render(request, 'edit_item.html', {'form': form})


@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, owner=request.user)
    item.delete()
    messages.success(request, 'Success')
    return redirect("item_list")

def categories_list(request):
    categories = Category.objects.select_related('parent').all()
    return render(request, 'categories/list.html', {'categories': categories})

@login_required
def request_category_create(request):
    if request.method == 'POST':
        form = CategoryRequestForm(request.POST)
        if form.is_valid():
            cat_req = form.save(commit=False)
            cat_req.user = request.user
            cat_req.save()

            messages.success(request, "Дякуємо! Ваш запит на створення категорії надіслано адміністратору.")

            # опційно: відправити адмінам лист
            staff_emails = list(User.objects.filter(is_staff=True).exclude(email='').values_list('email', flat=True))
            if staff_emails:
                subject = f"Новий запит на категорію: {cat_req.name}"
                url = request.build_absolute_uri(reverse('admin:app_categoryrequest_change', args=(cat_req.pk,)))
                body = f"Користувач {request.user.get_username()} запропонував категорію '{cat_req.name}'.\n\nПереглянути в адмінці: {url}"
                try:
                    send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, staff_emails, fail_silently=True)
                except Exception:
                    pass

            return redirect('categories:list')
    else:
        form = CategoryRequestForm()
    return render(request, 'categories/request_create.html', {'form': form})