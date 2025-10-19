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
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/history/', views.deal_history, name='history'),
path("update-avatar/", views.update_avatar, name="update_avatar"),
path("clear-avatar/", views.clear_avatar, name="clear_avatar"),
    path("shared_order/create/", views.create_shared_order, name="create_shared_order"),
    path("shared_order/<uuid:order_id>/", views.shared_order_detail, name="shared_order_detail"),
    path("shared_order/<uuid:order_id>/contribute/", views.contribute_to_shared_order, name="contribute_to_shared_order"),
    path("shared_order/<uuid:order_id>/finalize/", views.finalize_shared_order, name="finalize_shared_order"),
    path("shared_order/<uuid:order_id>/cancel/", views.cancel_shared_order, name="cancel_shared_order"),
    path("rate_item/<int:item_id>/<int:rating>/", views.rate_item, name="rate_item"),]
