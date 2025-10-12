from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from item.views import item_list

app_name = 'bns'
urlpatterns = [
    path("home/", item_list, name="home"),
    path("promo/apply/", views.apply_promo_code, name="apply_promo"),
    path("checkout/<int:item_id>/", views.checkout_with_promo, name="checkout"),
    path('analytics/', views.owner_analytics, name='owner_analytics'),
    path("register/", views.register_view, name="register"),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]
