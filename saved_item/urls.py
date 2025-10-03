from django.urls import path
from . import views

urlpatterns = [
    path("saved/<int:object_id>/<int:content_type>/", views.save_item, name="save_item"),
    path("saved_list", views.list_saved, name="saved_list"),
    path("saved/delete/<int:pk>", views.delete_saved, name="delete_saved")
]