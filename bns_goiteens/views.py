from django.shortcuts import render
from .models import Product

def home(request):
    products = Product.objects.all()

    category = request.GET.get('category')
    if category:
        products = products.filter(category=category)

    sort = request.GET.get('sort')
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')
    elif sort == 'name':
        products = products.order_by('name')

    return render(request, "base.html", {"products": products})