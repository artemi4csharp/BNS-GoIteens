from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_cart_objects, name='cart'),
    path('add_to_cart/<int:object_id>/<int:content_type_id>/', views.add_to_cart, name='add_to_cart'),
    path('delete_from_cart/<int:object_id>/<int:content_type_id>/', views.delete_cart_objects, name='delete_from_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order_success/<uuid:order_id>/', views.order_success_view, name='order_success'),
    path('remove_all_from_cart/<int:object_id>/<int:content_type_id>/', views.remove_all_from_cart, name='remove_all_from_cart'),
    path('apply_promo/', views.apply_promo_code, name='apply_promo'),

]
