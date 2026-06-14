from django.urls import path
from .views import *

urlpatterns = [
    path('', home, name='home'),
    path('start-chat/<str:username>/',get_or_create_chatroom,name='start-chat'),
    path('chat/room/<str:chatroom_name>/',chat_view,name='chatroom'),
    path('private/',private_chats_menu,name='private-chat-menu'),
    path('private/search/',search_private_chats,name='chat-search'),
    path('group/create/',create_group_chat,name='create-group-chat'),
    path('group/search/',search_group_chat,name='group-search'),
    path('group/leave/<str:chatroom_name>/',leave_group,name='leave-group'),
    path('group/verify-password/<str:chatroom_name>/',verify_password,name='verify-group-password'),
]