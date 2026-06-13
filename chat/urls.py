from django.urls import path
from .views import *

urlpatterns = [
    path('', chat_view, name='home'),
    path('start-chat/<str:username>/',get_or_create_chatroom,name='start-chat'),
    path('chat/room/<str:chatroom_name>/',chat_view,name='chatroom'),
    path('private/',private_chats_menu,name='private-chat-menu'),
    path('private/search/',search_private_chats,name='chat-search')
]