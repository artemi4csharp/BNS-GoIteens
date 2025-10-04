from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType


@login_required
def add_to_cart(request, object_id, content_type_id):
    

    cart = request.session.get('cart', {'offers':[]})
    
    for offer in cart['offers']:
        if offer['content_type_id'] == content_type_id and offer['object_id'] == object_id:
            offer['quantity'] += 1
            break
    else:
        cart['offers'].append({'content_type_id':content_type_id, 'object_id':object_id, 'quantity': 1})
    request.session['cart'] = cart
    request.session.modified = True
    return redirect('item:item_list')

@login_required
def get_cart_objects(request):
    cart = request.session.get('cart', {'offers': []})
    items = []
    
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
        except model_class.DoesNotExist:
            continue
    return render(request, 'cart.html', {'items': items})


@login_required
def delete_cart_objects(request, object_id, content_type_id):
    
    cart = request.session.get('cart', {'offers':[]})
    
    for offer in cart['offers']:
        if offer['content_type_id'] == content_type_id and offer['object_id'] == object_id:
            cart['offers'].remove(offer)
            break

    request.session['cart'] = cart
    request.session.modified = True
    return redirect('cart')