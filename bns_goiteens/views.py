from decimal import Decimal
from .models import PromoCode, Item, User, SharedOrder, SharedOrderItem, Order, OrderItem, SharedOrderContribution, DealHistory
from .decorators import promo_admin_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, SharedOrderForm, SharedOrderContributionForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .forms import PromoCodeForm, ProfileUpdateForm
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from .forms import SharedOrderForm, SharedOrderContributionForm
from .models import SharedOrder, SharedOrderItem
from bns_goiteens.models import OwnerAnalytics
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.contenttypes.models import ContentType
from .models import Item, Rating

# Create your views here.

from .models import Item


def home(request):
    items = Item.objects.all()

    category = request.GET.get('category')
    if category:
        items = items.filter(category=category)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        items = items.order_by('price')
    elif sort == 'price_desc':
        items = items.order_by('-price')
    elif sort == 'name':
        items = items.order_by('name')

    return render(request, "base.html", {"item": items})


@login_required
def apply_promo_code(request):
    if request.method == 'POST':
        form = PromoCodeForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data['code']
            try:
                promo = PromoCode.objects.get(code=code)
                result = promo.apply_promo(request.user)
                if result['success']:
                    messages.success(request, result['message'])
                    if result.get('balance_added'):
                        return redirect('bns:home')
                else:
                    messages.error(request, result['message'])
            except PromoCode.DoesNotExist:
                messages.error(request, 'Промокод не знайдено')
    else:
        form = PromoCodeForm()

    return render(request, 'promo/apply_promo.html', {'form': form})


@login_required
def checkout_with_promo(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    promo_form = PromoCodeForm()
    final_price = item.price

    if request.method == 'POST':
        if 'apply_promo' in request.POST:
            promo_form = PromoCodeForm(request.POST)
            if promo_form.is_valid():
                code = promo_form.cleaned_data['code']
                try:
                    promo = PromoCode.objects.get(code=code)
                    if promo.promo_type == 'discount':
                        result = promo.apply_promo(request.user, order_amount=item.price)
                        if result['success']:
                            final_price = result['new_amount']
                            messages.success(request, result['message'])
                            request.session['promo_code'] = code
                        else:
                            messages.error(request, result['message'])
                    else:
                        messages.error(request, 'Цей промокод не підходить для знижки на товар')
                except PromoCode.DoesNotExist:
                    messages.error(request, 'Промокод не знайдено')

        elif 'buy_item' in request.POST:
            promo_code = request.session.get('promo_code')
            promo = None
            if promo_code:
                try:
                    promo = PromoCode.objects.get(code=promo_code)
                except PromoCode.DoesNotExist:
                    pass

            price_to_pay = item.price
            if promo and promo.promo_type == 'discount' and promo.is_valid():
                result = promo.apply_promo(request.user, order_amount=item.price)
                if result['success']:
                    price_to_pay = result['new_amount']

            if request.user.balance >= price_to_pay:
                request.user.deduct_balance(price_to_pay)

                cashback_amount = price_to_pay * Decimal('0.05')  # 5% кешбек
                request.user.add_balance(cashback_amount)

                if 'promo_code' in request.session:
                    del request.session['promo_code']

                messages.success(request, f'Товар куплено! Кешбек {cashback_amount} грн додано до вашого балансу.')
                return redirect('item:item_list')
            else:
                messages.error(request, 'Недостатньо коштів на балансі')

    context = {
        'item': item,
        'promo_form': promo_form,
        'final_price': final_price,
    }
    return render(request, 'promo/checkout.html', context)

def owner_analytics(request):
    analytics, created = OwnerAnalytics.objects.get_or_create(owner=request.user)
    return render(request, 'owner_analytics.html', {'analytics': analytics})

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Ваш акаунт успішно створено!')
            return redirect('bns:home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})


@login_required
def profile_view(request):
    analytics, created = OwnerAnalytics.objects.get_or_create(owner=request.user)

    if request.method == 'POST':
        if 'activate_promo' in request.POST:
            promo_form = PromoCodeForm(request.POST)
            if promo_form.is_valid():
                code = promo_form.cleaned_data['code']
                try:
                    promo = PromoCode.objects.get(code=code)
                    result = promo.apply_promo(request.user)
                    if result['success']:
                        messages.success(request, result['message'])
                    else:
                        messages.error(request, result['message'])
                except PromoCode.DoesNotExist:
                    messages.error(request, 'Промокод не знайдено')
            return redirect('bns:profile')

        elif 'update_profile' in request.POST:
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Профіль успішно оновлено!')
                return redirect('bns:profile')
            else:
                messages.error(request, 'Помилка при оновленні профілю!')

    promo_form = PromoCodeForm()
    profile_form = ProfileUpdateForm(instance=request.user)

    context = {
        'promo_form': promo_form,
        'profile_form': profile_form,
        'analytics': analytics,  # Додаємо аналітику в контекст
    }
    return render(request, 'profile.html', context)


@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваш профіль успішно оновлено!')
            return redirect('bns:profile')
    else:
        form = ProfileUpdateForm(instance=request.user)

    return render(request, 'edit_profile.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Ви успішно вийшли з акаунту.')
    return redirect('bns:home')


@login_required
def update_avatar(request):
    if request.method == "POST" and request.FILES.get("avatar"):
        avatar = request.FILES["avatar"]
        request.user.avatar = avatar
        request.user.save()
        messages.success(request, "Аватар успішно оновлено!")
    else:
        messages.error(request, "Не вдалося оновити аватар.")
    return redirect("bns:profile")



@login_required
def clear_avatar(request):
    if request.method == "POST":
        if request.user.avatar:
            request.user.avatar.delete(save=True)
        request.user.avatar = None
        request.user.save()
    return redirect("bns:profile")


@login_required
def create_shared_order(request):
    cart = request.session.get('cart', {'offers': []})

    if not cart['offers']:
        messages.error(request, 'Ваш кошик порожній')
        return redirect('cart')

    items = []
    total_price = Decimal('0.00')

    for offer in cart['offers']:
        ct = ContentType.objects.get_for_id(offer['content_type_id'])
        model_class = ct.model_class()
        try:
            obj = model_class.objects.get(id=offer['object_id'])
            item_total = Decimal(str(obj.price)) * offer['quantity']
            items.append({
                'object': obj,
                'quantity': offer['quantity'],
                'total': item_total
            })
            total_price += item_total
        except model_class.DoesNotExist:
            continue

    if request.method == 'POST':
        form = SharedOrderForm(request.POST)
        if form.is_valid():
            shared_order = form.save(commit=False)
            shared_order.creator = request.user
            shared_order.total_amount = total_price
            shared_order.payment_method = 'balance'
            shared_order.save()

            for item in items:
                SharedOrderItem.objects.create(
                    shared_order=shared_order,
                    item=item['object'],
                    quantity=item['quantity'],
                    price=item['object'].price
                )

            request.session['cart'] = {'offers': []}
            request.session.modified = True

            messages.success(request, 'Спільне замовлення створено успішно!')
            return render(request, 'shared_order/order_success.html', {'shared_order': shared_order})
    else:
        initial_data = {
            'phone': request.user.phone or ''
        }
        form = SharedOrderForm(initial=initial_data)

    context = {
        'items': items,
        'total_price': total_price,
        'form': form
    }

    return render(request, 'shared_order/create.html', context)


@login_required
def shared_order_detail(request, order_id):
    shared_order = get_object_or_404(SharedOrder, id=order_id)

    if (shared_order.creator != request.user and
            not shared_order.contributions.filter(user=request.user).exists()):
        messages.error(request, 'У вас немає доступу до цього замовлення')
        return redirect('bns:home')

    contributions = shared_order.contributions.all()
    user_contribution = contributions.filter(user=request.user).first()

    context = {
        'shared_order': shared_order,
        'contributions': contributions,
        'user_contribution': user_contribution,
        'remaining_amount': shared_order.remaining_amount(),
        'progress_percentage': shared_order.progress_percentage()
    }

    return render(request, 'shared_order/detail.html', context)


@login_required
def contribute_to_shared_order(request, order_id):
    shared_order = get_object_or_404(SharedOrder, id=order_id)

    if shared_order.status != 'collecting':
        messages.error(request, 'Це замовлення більше не приймає внески')
        return redirect('bns:shared_order_detail', order_id=shared_order.id)

    existing_contribution = shared_order.contributions.filter(user=request.user).first()
    if existing_contribution:
        messages.error(request, 'Ви вже зробили внесок у це замовлення')
        return redirect('bns:shared_order_detail', order_id=shared_order.id)

    if request.method == 'POST':
        form = SharedOrderContributionForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']

            max_amount = shared_order.remaining_amount()
            if amount > max_amount:
                amount = max_amount
                messages.info(request, f'Ваш внесок було скорочено до {amount} грн, щоб не перевищити необхідну суму')

            if request.user.balance >= amount:
                request.user.balance -= amount
                request.user.save()

                SharedOrderContribution.objects.create(
                    shared_order=shared_order,
                    user=request.user,
                    amount=amount,
                    payment_method='balance'
                )

                shared_order.collected_amount += amount
                shared_order.save()

                messages.success(request, f'Ваш внесок {amount} грн успішно зараховано!')

                if shared_order.is_fully_paid():
                    messages.success(request, 'Необхідна сума зібрана! Тепер можна підтвердити оплату.')
            else:
                messages.error(request, 'Недостатньо коштів на балансі')
                return redirect('bns:contribute_to_shared_order', order_id=shared_order.id)

            return redirect('bns:shared_order_detail', order_id=shared_order.id)
    else:
        initial_amount = min(
            Decimal('100'),
            shared_order.remaining_amount()
        )
        form = SharedOrderContributionForm(initial={'amount': initial_amount})

    context = {
        'shared_order': shared_order,
        'form': form,
        'remaining_amount': shared_order.remaining_amount()
    }

    return render(request, 'shared_order/contribute.html', context)

@login_required
def finalize_shared_order(request, order_id):
    shared_order = get_object_or_404(SharedOrder, id=order_id)

    if shared_order.creator != request.user:
        messages.error(request, 'Тільки творець замовлення може його завершити')
        return redirect('bns:shared_order_detail', order_id=shared_order.id)

    if not shared_order.is_fully_paid():
        messages.error(request, 'Ще не зібрано повну суму для оформлення замовлення')
        return redirect('bns:shared_order_detail', order_id=shared_order.id)

    order = Order.objects.create(
        user=shared_order.creator,
        total_amount=shared_order.total_amount,
        status='paid',
        shipping_address=f"{shared_order.region}, м. {shared_order.city}, вул. {shared_order.street}, буд. {shared_order.building}",
        phone=shared_order.phone,
        payment_method='balance'  # Завжди баланс
    )

    for shared_item in shared_order.sharedorderitem_set.all():
        OrderItem.objects.create(
            order=order,
            item=shared_item.item,
            quantity=shared_item.quantity,
            price=shared_item.price
        )

        shared_item.item.owner.income += shared_item.price * shared_item.quantity
        shared_item.item.owner.save()

    shared_order.status = 'processing'
    shared_order.save()

    messages.success(request, 'Замовлення успішно оформлено та оплачено!')
    return redirect('bns:shared_order_detail', order_id=shared_order.id)


@login_required
def cancel_shared_order(request, order_id):
    shared_order = get_object_or_404(SharedOrder, id=order_id)

    if shared_order.creator != request.user:
        messages.error(request, 'Тільки творець замовлення може його скасувати')
        return redirect('bns:shared_order_detail', order_id=shared_order.id)

    if shared_order.status not in ['collecting', 'paid']:
        messages.error(request, 'Це замовлення вже не можна скасувати')
        return redirect('bns:shared_order_detail', order_id=shared_order.id)

    for contribution in shared_order.contributions.all():
        contribution.user.balance += contribution.amount
        contribution.user.save()

    shared_order.status = 'cancelled'
    shared_order.save()

    messages.success(request, 'Спільне замовлення скасовано, кошти повернено учасникам')
    return redirect('bns:shared_order_detail', order_id=shared_order.id)


@require_POST
def rate_item(request, item_id, rating):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'error': 'Необхідно увійти в систему'}, status=401)

    if rating < 1 or rating > 5:
        return JsonResponse({'success': False, 'error': 'Неправильний рейтинг'}, status=400)

    try:
        item = Item.objects.get(id=item_id)
        content_type = ContentType.objects.get_for_model(Item)

        rating_obj, created = Rating.objects.update_or_create(
            user=request.user,
            content_type=content_type,
            object_id=item_id,
            defaults={'value': rating}
        )

        new_avg = item.average_rating()

        return JsonResponse({
            'success': True,
            'message': f'Рейтинг {rating} збережено',
            'new_avg': new_avg
        })

    except Item.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Товар не знайдено'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)

@login_required
def deal_history(request):
    history = DealHistory.objects.filter(user=request.user).order_by('-timestamp')
    return render(request, 'history.html', {'history': history})