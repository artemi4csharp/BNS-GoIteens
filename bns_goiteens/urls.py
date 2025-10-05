from django.urls import path
from . import views
from item.views import item_list 

app_name = 'bns'
urlpatterns = [
    path("home/", item_list, name="home"),
    path("promo/apply/", views.apply_promo_code, name="apply_promo"),
    path("checkout/<int:item_id>/", views.checkout_with_promo, name="checkout"),
]
