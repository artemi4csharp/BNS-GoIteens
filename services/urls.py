from django.urls import path
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
]
