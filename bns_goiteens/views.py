from decimal import Decimal
from .models import PromoCode, Item, User
from .decorators import promo_admin_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from .models import PromoCode, User
from .forms import PromoCodeForm, ProfileUpdateForm

# Create your views here.
def home(request):
    return render(request, "base.html")

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

    return render(request, "base.html", {"item": item})
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
                    # Якщо промокод на поповнення балансу, перенаправити на сторінку балансу
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


@promo_admin_required
def create_promo_code(request):
    if request.method == 'POST':
        pass
    else:
        pass
    return render(request, 'promo/create_promo.html')

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
    if request.method == 'POST':
        # Обробка форми промокоду
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

        # Обробка форми редагування профілю
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
    }
    return render(request, 'profile.html', context)



# Додай вьюху для логауту
def logout_view(request):
    logout(request)
    messages.success(request, 'Ви успішно вийшли з акаунту.')
    return redirect('bns:home')