from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('support/create/', views.create_support_session, name='create_support_session'),
    path('support/sessions/', views.user_support_sessions, name='user_support_sessions'),
    path('support/session/<int:session_id>/', views.support_session_detail, name='support_session_detail'),

    path('agent/dashboard/', views.agent_dashboard, name='agent_dashboard'),
    path('agent/session/<int:session_id>/', views.agent_session_detail, name='agent_session_detail'),
    path('agent/session/<int:session_id>/assign/', views.assign_session, name='assign_session'),
    path('session/<int:session_id>/close/', views.close_session, name='close_session'),
    path("room/", views.chat_view, name="chat_room"),
]
