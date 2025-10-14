from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from decimal import Decimal
from .models import PromoCode, Item, Service
from .forms import PromoCodeForm



def home(request):
    items = Item.objects.all()
    services = Service.objects.all()

    last_seen_items = request.session.get("item_history", [])
    last_seen_services = request.session.get("service_history", [])

    items_in_history = sorted(
        Item.objects.filter(pk__in=last_seen_items),
        key=lambda s: -last_seen_items.index(s.pk)
    )
    services_in_history = sorted(
        Service.objects.filter(pk__in=last_seen_services),
        key=lambda s: -last_seen_services.index(s.pk)
    )

    return render(request, "home.html", {
        "items": items,
        "services": services,
        "items_in_history": items_in_history,
        "services_in_history": services_in_history,
    })


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