from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required 
from bns_goiteens.models import Item, Rating, Service
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import ItemCreationForm, ItemEditForm, RatingForm, CategoryRequestForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Category
from django.contrib.auth.models import User


# def item_list(request):
#     items = Item.objects.all()
#     return render(request, 'item_list.html', {'items': items})

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    content_type = ContentType.objects.get_for_model(Item)

    viewed_items = request.COOKIES.get('viewed_items', '')
    viewed_ids = viewed_items.split(',') if viewed_items else []

    if str(pk) not in viewed_ids:
        item.views += 1
        item.save(update_fields=['views'])
        viewed_ids.append(str(pk))

    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            content_type=content_type,
            object_id=item.id,
            user=request.user
        ).first()
    else:
        user_rating = None

    form = RatingForm(request.POST or None, instance=user_rating)

    if request.method == 'POST':
        if form.is_valid() and request.user.is_authenticated:
            rating = form.save(commit=False)
            rating.user = request.user
            rating.content_object = item
            rating.save()
            messages.success(request, 'Success')
            return redirect('item_detail', pk=item.pk)
        else:
            messages.error(request, 'Error')

    response = render(request, 'item_detail.html', {
        'item': item,
        'form': form,
    })

    # Захист через кукі від накруток
    response.set_cookie('viewed_items', ','.join(viewed_ids), max_age=60*60*24*10)

    return response


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


def item_list(request):
    query = request.GET.get("q")
    category = request.GET.get("category")
    owner = request.GET.get("owner")

    items = Item.objects.all()
    services = Service.objects.all()

    if query:
        items = items.filter(name__icontains=query) | items.filter(description__icontains=query)
        services = services.filter(name__icontains=query) | services.filter(description__icontains=query)

    if category:
        items = items.filter(category_id=category)
        services = services.filter(category_id=category)

    if owner:
        items = items.filter(owner__id=owner) | items.filter(owner__username__icontains=owner)
        services = services.filter(owner__id=owner) | services.filter(owner__username__icontains=owner)

    return render(request, "item_list.html", {
        "items": items,
        "services": services
    })


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