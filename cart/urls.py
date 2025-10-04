from django.urls import path
from . import views

urlpatterns = [
    path('cart', views.get_cart_objects, name='cart'),
    path('add_to_cart/<int:object_id>/<int:content_type_id>/', views.add_to_cart, name='add_to_cart'),
    path(
    'delete_from_cart/<int:object_id>/<int:content_type_id>/', views.delete_cart_objects, name='delete_from_cart'), 
]