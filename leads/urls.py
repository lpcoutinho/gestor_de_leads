from django.urls import path
from .views import lead_list, send_message,send_message_and_update_status, send_message_to_all

urlpatterns = [
    path('', lead_list, name='lead_list'),
    path('send_message/', send_message, name='send_message'),
    path('send_message/<int:lead_id>/', send_message_and_update_status, name='send_message'),
    path('send_message_to_all/', send_message_to_all, name='send_message_to_all'),
]
