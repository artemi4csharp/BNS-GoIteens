from django.urls import path
from . import views

app_name = 'item'

urlpatterns = [
    path('list/', views.item_list, name='item_list'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:content_type_id>/<int:object_id>/complaint/', views.file_complaint, name='file_complaint'),
]
