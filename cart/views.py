from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import uuid
import requests
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from decimal import Decimal
from bns_goiteens.models import Order, OrderItem


@login_required
def add_to_cart(request, object_id, content_type_id):
    cart = request.session.get('cart', {'offers': []})

    for offer in cart['offers']:
        if offer['content_type_id'] == content_type_id and offer['object_id'] == object_id:
            offer['quantity'] += 1
            break
    else:
        cart['offers'].append({
            'content_type_id': content_type_id,
            'object_id': object_id,
            'quantity': 1
        })

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Товар додано до кошика'})

    return redirect('item:item_list')


@login_required
def get_cart_objects(request):
    cart = request.session.get('cart', {'offers': []})
    items = []
    total_price = 0
    total_quantity = 0

    for offer in cart['offers']:
        ct = ContentType.objects.get_for_id(offer['content_type_id'])
        model_class = ct.model_class()
        try:
            obj = model_class.objects.get(id=offer['object_id'])
            items.append({
                'object': obj,
                'quantity': offer['quantity'],
                'type': ct.model
            })
            total_price += float(obj.price) * offer['quantity']
            total_quantity += offer['quantity']
        except model_class.DoesNotExist:
            continue

    context = {
        'items': items,
        'total_price': round(total_price, 2),
        'total_quantity': total_quantity
    }

    return render(request, 'cart.html', context)


@login_required
def delete_cart_objects(request, object_id, content_type_id):
    cart = request.session.get('cart', {'offers': []})

    for i, offer in enumerate(cart['offers']):
        if offer['content_type_id'] == content_type_id and offer['object_id'] == object_id:
            if offer['quantity'] > 1:
                offer['quantity'] -= 1
            else:
                cart['offers'].pop(i)
            break

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Товар видалено з кошика'})

    return redirect('cart')

@login_required
def remove_all_from_cart(request, object_id, content_type_id):
    cart = request.session.get('cart', {'offers': []})

    cart['offers'] = [offer for offer in cart['offers']
                     if not (offer['content_type_id'] == content_type_id and offer['object_id'] == object_id)]

    request.session['cart'] = cart
    request.session.modified = True

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'success': True, 'message': 'Товар видалено з кошика'})

    return redirect('cart')

@login_required
def checkout_view(request):
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
        payment_method = request.POST.get('payment_method')

        if payment_method == 'balance':
            if request.user.balance >= total_price:
                request.user.balance -= total_price
                request.user.save()

                order = Order.objects.create(
                    user=request.user,
                    total_amount=total_price,
                    shipping_address=request.POST.get('shipping_address', ''),
                    phone=request.POST.get('phone', request.user.phone or ''),
                    payment_method='balance',
                    status='paid'
                )

                for item in items:
                    OrderItem.objects.create(
                        order=order,
                        item=item['object'],
                        quantity=item['quantity'],
                        price=item['object'].price
                    )

                    item['object'].owner.income += item['object'].price * item['quantity']
                    item['object'].owner.save()

                request.session['cart'] = {'offers': []}
                request.session.modified = True

                messages.success(request, f'Замовлення #{order.id} успішно оплачено з балансу!')
                return redirect('order_success', order_id=order.id)
            else:
                messages.error(request, 'Недостатньо коштів на балансі для оплати замовлення')
        else:
            payment_data = {
                'amount': float(total_price),
                'currency': 'UAH',
                'description': f'Оплата замовлення #{uuid.uuid4().hex[:8]}',
                'customer_email': request.user.email,
                'customer_phone': request.user.phone or '',
                'payment_method': payment_method
            }

            try:
                payment_response = {
                    'status': 'success',
                    'transaction_id': f'test_{uuid.uuid4().hex[:12]}',
                    'message': 'Оплата успішно оброблена'
                }

                if payment_response['status'] == 'success':
                    order = Order.objects.create(
                        user=request.user,
                        total_amount=total_price,
                        shipping_address=request.POST.get('shipping_address', ''),
                        phone=request.POST.get('phone', request.user.phone or ''),
                        payment_method=payment_method,
                        transaction_id=payment_response['transaction_id'],
                        status='paid'
                    )

                    for item in items:
                        OrderItem.objects.create(
                            order=order,
                            item=item['object'],
                            quantity=item['quantity'],
                            price=item['object'].price
                        )

                        item['object'].owner.income += item['object'].price * item['quantity']
                        item['object'].owner.save()

                    request.session['cart'] = {'offers': []}
                    request.session.modified = True

                    messages.success(request,
                                     f'Замовлення #{order.id} успішно оформлено! {payment_response["message"]}')
                    return redirect('order_success', order_id=order.id)
                else:
                    messages.error(request, 'Помилка при обробці платежу')

            except Exception as e:
                messages.error(request, f'Помилка при оформленні замовлення: {str(e)}')

    context = {
        'items': items,
        'total_price': total_price,
        'user': request.user
    }

    return render(request, 'checkout.html', context)

@login_required
def order_success_view(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_success.html', {'order': order})