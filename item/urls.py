from django.urls import path
from . import views

app_name = 'item'

urlpatterns = [
    path('list/', views.item_list, name='item_list'),
    path('<int:pk>/', views.item_detail, name='item_detail'),
    path('<int:content_type_id>/<int:object_id>/complaint/', views.file_complaint_message, name='file_complaint'),
    path('item_list/', views.item_list, name='item_list'),
    path('item/<int:pk>/', views.item_detail, name='item_detail'),
    path('create_item/', views.create_item, name='create_item'),
    path('create_location/', views.create_location, name='create_location'),
    path('edit_item/<int:pk>/', views.edit_item, name='edit_item'),
    path('delete_item/<int:pk>/', views.delete_item, name='delete_item'),

    path('request/', views.request_category_create, name='request_create'),
]
