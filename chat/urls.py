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
    path('support/history/', views.support_history, name='support_history'),
    path("room/<int:pk>", views.chat_view, name="chat_room"),

    path("room/<int:other_user_id>/", views.chat_view, name="chat_room"),
    path("history/", views.user_chat_history, name="user_chat_history"),
    path("message/<int:message_id>/complaint/", views.file_complaint_message, name="file_complaint_message"),
]
