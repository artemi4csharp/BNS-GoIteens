from django.shortcuts import render
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
