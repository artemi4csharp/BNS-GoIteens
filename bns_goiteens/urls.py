from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'bns'
urlpatterns = [
    path("home/", views.home, name="home"),
    path("promo/apply/", views.apply_promo_code, name="apply_promo"),
    path("checkout/<int:item_id>/", views.checkout_with_promo, name="checkout"),
    path("register/", views.register_view, name="register"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
]
