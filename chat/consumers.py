from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from .models import ChatGroup,Message
from django.template.loader import render_to_string
from asgiref.sync import async_to_sync
import json

class ChatRoomConsumer(WebsocketConsumer):
    def connect(self):
        self.user=self.scope['user']
        if not self.user.is_authenticated:
            self.close()
            return
        self.room_name=self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom=get_object_or_404(ChatGroup,group_name=self.room_name)
        if self.chatroom.is_private and self.user not in self.chatroom.members.all():
            self.close()
            return
        async_to_sync(self.channel_layer.group_add)(
            self.room_name,
            self.channel_name
        )
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()

        self.accept()

    def disconnect(self,close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_name,
            self.channel_name)
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count()

    

    def receive(self,text_data):
        message=json.loads(text_data)['body'].strip()
        if not message:
            return
        message=Message.objects.create(
            group=self.chatroom,
            author=self.user,
            body=message
        )
        self.chatroom.save(
            update_fields=['updated_at']
        )

        event={
            'type':'message_handler',
            'message_id':message.id,
        }
        
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,event)
        
    def message_handler(self,event):
        message_id=event['message_id']
        message=Message.objects.get(id=message_id)
        context={
            'chat_message':message,
            'user':self.user
        }
        html=render_to_string('chat/partials/message.html',context)
        self.send(text_data=f"""
                <ul id="chat_messages" hx-swap-oob="beforeend">
                    {html}
                </ul>
                """)
        
    def update_online_count(self):
        count=self.chatroom.users_online.count()-1
        event={
            'type':'online_count_handler',
            'count':count
        }
        async_to_sync(self.channel_layer.group_send)(
            self.room_name,event)
        
    def online_count_handler(self,event):
        count=event['count']
        html=render_to_string('chat/partials/online_count.html',{'count':count,'user':self.user})
        self.send(text_data=html)