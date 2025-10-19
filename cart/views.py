from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import uuid
import requests
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from decimal import Decimal
from bns_goiteens.models import Order, OrderItem, PromoCode
from django.views.decorators.csrf import csrf_exempt


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

    discount_info = request.session.get('cart_discount', {})

    context = {
        'items': items,
        'total_price': round(total_price, 2),
        'total_quantity': total_quantity,
        'discount_info': discount_info
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


@csrf_exempt
@login_required
def apply_promo_code(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            code = data.get('code', '').strip()

            if not code:
                return JsonResponse({
                    'success': False,
                    'message': 'Введіть промокод'
                })

            try:
                promo = PromoCode.objects.get(code=code)

                if not promo.is_valid():
                    return JsonResponse({
                        'success': False,
                        'message': 'Промокод недійсний або закінчився'
                    })

                cart = request.session.get('cart', {'offers': []})
                if not cart['offers']:
                    return JsonResponse({
                        'success': False,
                        'message': 'Кошик порожній'
                    })

                total_price = Decimal('0.00')
                items = []

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

                if promo.promo_type == 'discount':
                    discount_amount = total_price * (promo.value / 100)
                    final_price = total_price - discount_amount

                    request.session['cart_discount'] = {
                        'code': promo.code,
                        'type': 'discount',
                        'value': float(promo.value),
                        'discount_amount': float(discount_amount),
                        'original_price': float(total_price),
                        'final_price': float(final_price)
                    }
                    request.session.modified = True

                    return JsonResponse({
                        'success': True,
                        'message': f'Застосовано знижку {promo.value}%',
                        'discount_amount': float(discount_amount),
                        'original_price': float(total_price),
                        'final_price': float(final_price)
                    })

                elif promo.promo_type == 'free_item':
                    discount_amount = Decimal('0.00')
                    item_with_discount = None

                    for item in items:
                        obj = item['object']
                        if (promo.target_item and obj == promo.target_item) or \
                                (promo.target_category and obj.category == promo.target_category):
                            item_with_discount = item
                            discount_amount = item['total'] * Decimal('0.9')  # 90% знижка
                            break

                    if item_with_discount:
                        final_price = total_price - discount_amount

                        request.session['cart_discount'] = {
                            'code': promo.code,
                            'type': 'free_item',
                            'discount_amount': float(discount_amount),
                            'original_price': float(total_price),
                            'final_price': float(final_price),
                            'item_name': item_with_discount['object'].name
                        }
                        request.session.modified = True

                        return JsonResponse({
                            'success': True,
                            'message': f'Застосована знижка на товар "{item_with_discount["object"].name}"',
                            'discount_amount': float(discount_amount),
                            'original_price': float(total_price),
                            'final_price': float(final_price)
                        })
                    else:
                        return JsonResponse({
                            'success': False,
                            'message': 'Промокод не дійсний для товарів у кошику'
                        })

                elif promo.promo_type == 'balance':
                    return JsonResponse({
                        'success': False,
                        'message': 'Цей промокод призначений для поповнення балансу, а не для знижок'
                    })

                else:
                    return JsonResponse({
                        'success': False,
                        'message': 'Невідомий тип промокоду'
                    })

            except PromoCode.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'message': 'Промокод не знайдено'
                })

        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'message': 'Невірний формат запиту'
            })

    return JsonResponse({
        'success': False,
        'message': 'Метод не дозволений'
    })


@login_required
def checkout_view(request):
    cart = request.session.get('cart', {'offers': []})

    discount_info = request.session.get('cart_discount', {})
    discount_amount = discount_info.get('discount_amount', 0)

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

    if discount_amount > 0:
        total_price -= Decimal(str(discount_amount))
        if 'cart_discount' in request.session:
            del request.session['cart_discount']
            request.session.modified = True

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
