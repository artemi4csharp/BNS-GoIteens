from django.shortcuts import render, redirect
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.decorators import login_required
from bns_goiteens.models import Item, Rating, Service
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .forms import ItemCreationForm, ItemEditForm, RatingForm, CategoryRequestForm, CommentForm
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Category
from django.contrib.auth.models import User
from django.db.models import Avg
from .forms import ItemCreationForm, ItemEditForm, RatingForm
from django.views.decorators.http import require_POST
from bns_goiteens.models import Category

# def item_list(request):
#     items = Item.objects.all()
#     return render(request, 'item_list.html', {'items': items})
from django.db.models import Avg
from django.db.models import Count

def item_detail(request, pk):
    item = get_object_or_404(Item, pk=pk)
    content_type = ContentType.objects.get_for_model(Item)

    # -------- обновляем просмотры --------
    item.views += 1
    item.save(update_fields=['views'])

    # -------- обновляем историю просмотров в сессии --------
    item_history = request.session.get('item_history', [])

    if pk not in item_history:
        item_history.append(pk)
        if len(item_history) > 5:
            item_history = item_history[-5:]
        request.session['item_history'] = item_history
        request.session.modified = True
    # -------------------------------------

    # -------- рейтинг и комментарии --------
    all_ratings = Rating.objects.filter(content_type=content_type, object_id=item.id)
    avg_rating = all_ratings.aggregate(Avg('value'))['value__avg'] or 0
    total_reviews = all_ratings.count()

    rating_distribution = (
        all_ratings
        .values('value')
        .annotate(count=Count('id'))
        .order_by('-value')
    )

    rating_counts = {i: 0 for i in range(1, 6)}
    for entry in rating_distribution:
        rating_counts[int(entry['value'])] = entry['count']

    if total_reviews > 0:
        rating_percentages = {
            i: (rating_counts[i] / total_reviews) * 100 for i in range(1, 6)
        }
    else:
        rating_percentages = {i: 0 for i in range(1, 6)}

    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(
            content_type=content_type,
            object_id=item.id,
            user=request.user
        ).first()
    else:
        user_rating = None

    form = RatingForm(request.POST or None, instance=user_rating)
    if request.method == 'POST' and 'value' in request.POST:
        if form.is_valid() and request.user.is_authenticated:
            rating = form.save(commit=False)
            rating.user = request.user
            rating.content_object = item
            rating.save()
            messages.success(request, 'Ваша оцінка збережена!')
            return redirect('item:item_detail', pk=item.pk)
        else:
            messages.error(request, 'Помилка при збереженні оцінки.')

    form_comment = CommentForm(request.POST or None)
    if request.method == "POST" and 'text' in request.POST:
        if form_comment.is_valid() and request.user.is_authenticated:
            comment = form_comment.save(commit=False)
            comment.author = request.user
            comment.content_type = content_type
            comment.object_id = item.id
            comment.save()
            messages.success(request, "Коментар успішно додано!")
            return redirect('item:item_detail', pk=item.pk)
        else:
            messages.error(request, "Помилка: потрібно увійти в акаунт або заповнити поле тексту.")

    context = {
        'item': item,
        'form': form,
        'avg_rating': round(avg_rating, 1),
        'total_reviews': total_reviews,
        'rating_counts': rating_counts,
        'rating_percentages': rating_percentages,
        'form_comment': form_comment,
        'rating_stars': [5,4,3,2,1],
    }

    return render(request, 'view_item.html', context)

@login_required
def create_item(request):
    if request.method == 'POST':
        form = ItemCreationForm(request.POST, request.FILES)
        if form.is_valid():
            item = form.save(commit=False)
            item.owner = request.user
            item.save() 
            messages.success(request, 'Success')
            return redirect('item:item_list')
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
        return redirect('item:item_list')
    return render(request, 'edit.html', {'form': form})


@login_required
def delete_item(request, pk):
    item = get_object_or_404(Item, pk=pk, owner=request.user)
    item.delete()
    messages.success(request, 'Success')
    return redirect("item:item_list")


def item_list(request):
    query = request.GET.get("q")
    category = request.GET.get("category")
    owner = request.GET.get("owner")
    categories = Category.objects.filter(is_active=True)

    # -------- Пошук айтемів --------------
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
    # -------------------------------

    # Показує раніше переглянуті товари
    last_seen_items = request.session.get("item_history", [])
    items_in_history = sorted(
        Item.objects.filter(pk__in=last_seen_items),
        key=lambda s: -last_seen_items.index(s.pk)
    )
    # --------------End----------

    # ---------- Сортування айтемів --------------------
    sort = request.GET.get('sort') or request.session.get('sort')

    # -------------- Збереження сортування в сесії --------------
    if sort:
        request.session['sort'] = sort

    if sort == 'price_asc':
        items = items.order_by('price')
    elif sort == 'price_desc':
        items = items.order_by('-price')
    elif sort == 'name':
        items = items.order_by('name')
    # -------------------------------------

    return render(request, "item_list.html", {
        "items": items,
        "services": services,
        "items_in_history": items_in_history,
        "categories": categories
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