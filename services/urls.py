from django.urls import path
import views
from .views import (
    ServiceListView,
    ServiceDetailView,
    ServiceCreateView,
    ServiceUpdateView,
    ServiceDeleteView,
)

urlpatterns = [
    path("", ServiceListView.as_view(), name="service_list"),

    path("<int:pk>/", ServiceDetailView.as_view(), name="service_detail"),

    path("create/", ServiceCreateView.as_view(), name="service_create"),

    path("<int:pk>/edit/", ServiceUpdateView.as_view(), name="service_edit"),

    path("<int:pk>/delete/", ServiceDeleteView.as_view(), name="service_delete"),

    path('compare/add/<int:item_id>/', views.add_to_comparison, name='add_to_comparison'),

    path('compare/remove/<int:item_id>/', views.remove_from_comparison, name='remove_from_comparison'),

    path('compare/', views.get_comparison, name='get_comparison'),
]
