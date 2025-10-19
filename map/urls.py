from django.urls import path 
from . import views 

urlpatterns = [
    path('items_location/', views.items_location, name='items_location'),
    path('add_map_point/', views.add_map_point, name='add_map_point')]